stockrobot
==========

Is supposed to be a tool for stock predicitons.
So far consists of three logical parts:
scraper              /* scrapes webpages and tries to parse them with regards to publication date, title, article */
stock-value-importer /* takes a csv file from http://www.nasdaqomxnordic.com/ and imports it into the database */
stockbrowser         /* simplifies browsing articles related in time to stock value deviations */
stock-predictor
    word-frequency-predictor /* Tries to find any particular words that might occur more often in relation stock value deviations */

So far I have scraped all articles on Affärsvärlden, and tried to do a word-frequency analysis related to the ERIC_B stock. 
Yielding 0 prediction accuracy.. =) Who thought it would be that simple eh?
Next I will start looking into more sophisticated prediction techniques, basically inputing whole articles into a neural net and see what comes out the other end.
 
Beautification disclaimer:
Admittedly, this is not the prettiest of applications. This is *very* much a work in progress and main goal has really been to test various datamining and prediction techniques. Therefore the application is not strictly adherent to MVC pattern, and far from optimized.
 
