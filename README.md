# LondonHomeOfficePairsJuly2023

----------------------------------------------
London Home-Office-Pairs (HOP) project Read Me
----------------------------------------------

By Frederick Bertani - July 2023 (github.com/frederickbertani)

This project was designed as a proof of concept to demonstrate the potential and ease of allocating an ideal home location to any user-input office given a set of constraints.

The concept for this script stems from when an individual wants to find out what location best suits them for a new home given a new office location. 
A user inputs their office location (either via a postcode or coordinates or an address since all three are interchangeable using GoogleMaps Geocode API), and some user-input weights, which place the importance of certain variables of a user’s personal preference for their home. 
These user-input weights can be things such as:
-> rent = monthly rent price
-> commute_cost = time to office * transportation cost (Transport for London API)
-> grocery_cost = distance to grocery store * average grocery cost
-> restaurant_cost =  distance to nearby restaurants * average meal cost / number of nearby restaurants
-> crime_rate = rate of crimes in area
-> school_rating = rating of nearby schools (1-5 scale for example)

and from these normalised weights, a cost-effectiveness score is calculated for each postcode district in the database:
cost_effectiveness_score = w1 * commute_cost + w2 * rent + w3 * grocery_cost + w4 * restaurant_cost + w5 * crime_rate + w6 * school_rating + w7*1

Then the database is sorted to output the entries with the optimised cost effectiveness score, thus revealing the user’s ideal home/office pair.

For the purposes of demonstrating the proof of concept, a minimal database incorporating rent and commute costs was implemented.
Although it is easily scalable to include more and more data to personalise the user’s choice further.

In the script uploaded, there is a bottleneck at the point of retrieving the commute cost since it involves calling the TFL with a free API key, which has a maximum number of requests per minute. If this script were to be implemented for profit and have some revenue, it would be wise to invest in API keys which extend the number of requests per minute such that the user experience doesn’t suffer from the issue presented above.
