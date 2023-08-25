# This script is a demonstration optimising London Home-Office pairs for given input location and
# attribute weights. The London Rental data was obtained from the ONS; the ease of commute is calculated for 
# each postcode district from its geographical centre (which was worked out through data from the Ordinance 
# Survey's Code Point Open dataset) using the TFL API for journey cost and journey time.

# Please note: because of the free TFL API key limit, it is only possible to perform 500 requests per minute,
# any requests exceeding this will return null results and will not be included in the dataframe for the 
# cost function determination - this is fixed by obtaining an API key without a request limit.

import pandas as pd
import asyncio
import aiohttp

# Declare where your office is
Postcode2 = 'SW75BD' # must not include any spaces
W1 = 1 # weight related to the rent
W2 = 30 # weight related to the ease of commute: general rule of thumb W2 ~ 30*# of beds minimum
Bedroom = 'One Bedroom' # Number of bedrooms in property

# Load the full rents DataFrame
Rents_df = pd.read_csv('LondonRentalData_NSNR_ND_NoEmpty.csv')

# Select the number of bedrooms we are searching for
RelevantRents = Rents_df[Rents_df['Bedroom Category'] == Bedroom]
RelevantRents = RelevantRents.reset_index(drop=True) # reset index

# Load the Postcodes dataframe
Postcodes_df = pd.read_csv('PostcodesDataframe.csv')

# Load the TFL API key, which can be obtained from https://api.tfl.gov.uk/
PrimaryKey = '5f93905d21a34f0bbfb157b7308cc08b'
SecondaryKey = '3719e1512ccd47feb159ba0f9af0cbd5'

# Initialise the cost scores list
cost_scores = pd.DataFrame(columns=['Cost Scores'])

# Define the linear cost function
def costfunction(W1, W2, commute, rent):
    output_cost = W1*rent + W2*commute
    return output_cost

async def get_journey(session, postcode1, postcode2, api_key):

    url = f'https://api.tfl.gov.uk/journey/journeyresults/{postcode1}/to/{postcode2}?app_id={api_key}'
    async with session.get(url) as resp:
        data = await resp.json()
        if 'journeys' in data and 'duration' in data['journeys'][0] and 'fare' in data['journeys'][0]:
            journey = data['journeys'][0]
            duration = journey['duration']
            cost = journey['fare']['totalCost'] / 100
        else:
            cost = float('inf')
            duration = float('inf')
        return postcode1, duration, cost

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    # Load dataframes etc
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(len(RelevantRents)):
            PostcodeDistrict = RelevantRents.iloc[i, RelevantRents.columns.get_loc('Postcode District')]
            index1 = Postcodes_df.index[Postcodes_df['Postcode_x'] == PostcodeDistrict]
            index1 = index1[0]
            postcode1 = Postcodes_df.iloc[index1, Postcodes_df.columns.get_loc('Postcode_y')]# get postcode

            if i < len(RelevantRents)/3: 
                API_Key = ''
            elif i < 2*len(RelevantRents)/3:
                API_Key = PrimaryKey
            else:
                API_Key = SecondaryKey

            task = asyncio.ensure_future(get_journey(session, postcode1, Postcode2, API_Key))
            tasks.append(task)
        
        durations_costs = await asyncio.gather(*tasks)
        
        return durations_costs
        
loop = asyncio.get_event_loop()
durations_costs = loop.run_until_complete(main())

asyncio.run(main())

# Process results
for i, (postcode1, duration, cost) in enumerate(durations_costs):
    # Update cost_scores dataframe etc

    travel_ease = duration*cost
    rent1 = RelevantRents.iloc[i, RelevantRents.columns.get_loc('Mean')]
    rent1 = float(rent1.replace(",", ""))
    output_cost1 = costfunction(W1, W2, travel_ease, rent1)
    new_row = pd.DataFrame({'Cost Scores': [output_cost1]})
    cost_scores = pd.concat([cost_scores, new_row],ignore_index=True)

cost_scores = cost_scores.astype({'Cost Scores': 'single'})
min_idx = cost_scores['Cost Scores'].idxmin()
Best_Postcode = RelevantRents['Postcode District'].iloc[min_idx]

print('The best postcode for a place with', Bedroom, 'is', Best_Postcode)

