import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np

class Geocode:
    def __init__(self):
        # num = self.get_dist(1,6,4,2)
        # print(f"Dist: {num}")
        # self.dfA = pd.read_csv('listings-ma.csv')
        # self.test_loc(self.dfA, 0, 6)
        # self.test_loc(self.dfA, 0, 7)
        #self.test_plot()
        # self.run(pd.read_csv('listings-fl.csv'))
        # self.run(pd.read_csv('listings-ma.csv'))
        self.run(pd.read_csv('listings-il.csv'))
        # self.run(pd.read_csv('listings-nc.csv'))
        # self.run(pd.read_csv('listings-ny.csv'))
        # self.run(pd.read_csv('listings-tx.csv'))

    def run(self, dfA):
        # Loading airbnb csv
        #self.lat = self.dfA.iloc[0, 6]
        #print(lat)

        # Loading price csv
        self.dfC = pd.read_csv('realtor-data.csv')

        # Filter for only MA
        self.array = [[0 for _ in range(3)] for _ in range(len(self.dfC))]
        self.macount = 0
        for i in range(len(self.dfC)):
            if(self.dfC.iloc[i, 8]=="Illinois" and pd.notna(self.dfC.iloc[i, 9])):
                self.array[self.macount][0] = str(self.dfC.iloc[i, 0])
                self.array[self.macount][1] = float(self.dfC.iloc[i, 2])
                self.array[self.macount][2] = int(self.dfC.iloc[i, 9])
                self.array[self.macount][2] = str(self.array[self.macount][2])
                while(len(self.array[self.macount][2])<5):
                    self.array[self.macount][2] = "0"+self.array[self.macount][2]
                self.macount+=1
        self.array = self.array[:self.macount]
        # self.id = self.array[0][0]
        # self.cost = self.array[0][1]
        # self.zipcode = self.array[0][2]
        print(f"Number of IL Houses {len(self.array)} : {len(self.dfC)}")
        # self.line = f"{self.id}, {self.cost}, {self.zipcode}"
        # print(self.line)

        # Combine costs zones
        self.comb = [[0 for _ in range(3)] for _ in range(len(self.array))]
        self.count = 0
        for i in range(len(self.array)):
            self.zipcode = self.array[i][2]
            self.boolean = 0
            for j in range(len(self.comb)):
                if(self.zipcode == self.comb[j][0]):
                    self.boolean = 1
                    self.comb[j][2]+=1
                    self.comb[j][1] = float(self.comb[j][1]+self.array[i][1])
                    break
            if(self.boolean == 0):
                self.comb[self.count][0] = self.array[i][2]
                self.comb[self.count][1] = self.array[i][1]
                self.comb[self.count][2] = 1
                self.count+=1
        self.comb = self.comb[:self.count]
        for i in range(len(self.comb)):
            self.comb[i][1] = self.comb[i][1]/self.comb[i][2]

        print(f"Number of Represented Zip Codes {len(self.comb)} : {len(self.array)}")

        # Geocode convert
        self.coord = [[0 for _ in range(3)] for _ in range(len(self.comb))]
        # lat, lng = self.api_call(self.comb[0][0])
        # print(f"Lat: {lat}; Lng: {lng}")
        self.count = 0
        self.wcount = 0
        for i in range(len(self.comb)):
            #make api call
            lat, lng = self.api_call(self.comb[i][0])
            if lat == None:
                self.count+=1
            else:
                self.coord[i][0] = self.comb[i][0]
                self.coord[i][1] = lat
                self.coord[i][2] = lng
                self.comb[self.wcount][0] = self.comb[i][0]
                self.comb[self.wcount][1] = self.comb[i][1]
                self.comb[self.wcount][2] = self.comb[i][2]
                self.wcount+=1
        self.coord = self.coord[:self.wcount]
        self.comb = self.comb[:self.wcount]
        print(f"Number of centroids: {len(self.coord)}")
        #print(f"Lat: {self.coord[0][1]}; Lng: {self.coord[0][2]}")
        print(f"Failed calls: {self.count}")

        # Map and combine airbnbs with centorids
        self.mapComb = [[0 for _ in range(3)] for _ in range(len(dfA))]
        for i in range(len(dfA)):
            self.mapComb[i][0] = dfA.iloc[i, 0]
            minDist = float('inf')
            for j in range(len(self.coord)):
                dist = self.get_dist(dfA.iloc[i, 6], dfA.iloc[i, 7], self.coord[j] [1], self.coord[j][2])
                if dist<minDist:
                    minDist = dist
                    self.mapComb[i][1] = self.coord[j][0]
                    self.mapComb[i][2] = dist

        # Reduce to num AirBnB per centroid
        self.red = [[0 for _ in range(2)] for _ in range(len(self.mapComb))]
        self.count = 0
        for i in range(len(self.mapComb)):
            all_in = 0
            #print(self.mapComb[i][2])
            if self.mapComb[i][2] > 0.005: #approximately the diameter of average boston zipcode+a bit as can affect outside of zip
                continue
            for j in range(len(self.red)):
                if self.red[j][0] == self.mapComb[i][1]:
                    self.red[j][1]+=1
                    all_in = 1
                    break
            if all_in == 0:
                self.red[self.count][0] = self.mapComb[i][1]
                self.red[self.count][1] = 1
                self.count+=1
        self.red = self.red[:self.count]
        
        # red has zipcode, numofAirbnb and comb has zipcode, avg cost, and number of houses in zip considered
        print("_________________________")
        print("---------Results---------")
        print("_________________________")
        print(f"Size of red: {len(self.red)}; Size of comb: {len(self.comb)}")
        self.results = np.zeros((len(self.red), 3))
        count = 0
        for i in range(len(self.red)):
            for j in range(len(self.comb)):
                if(self.red[i][0]==self.comb[j][0]):
                    print(f"Zip Code: {self.red[i][0]}; # of AirBnB: {self.red[i][1]}; Average Cost: {self.comb[j][1]}")
                    count = count + self.red[i][1]
                    self.results[i][0] = self.red[i][1]
                    self.results[i][1] = self.comb[j][1]
                    self.results[i][2] = self.red[i][0]
                    if self.red[i][0] != self.comb[j][0]:  
                        print("Failing")
                    break
        print(f"Number of AirBnBs Considered: {count}")
        self.results = self.results[self.results[:, 0].argsort()]
        xpoints = self.results[:, 0]
        ypoints = self.results[:, 1]
        labels = self.results[:, 2]
        for i, label in enumerate(labels):
            slabel = str(int(label))
            while len(slabel) < 5:
                slabel = "0"+slabel
            plt.annotate(slabel, (xpoints[i], ypoints[i]), xytext=(5, 5), textcoords="offset points")
        plt.scatter(xpoints, ypoints)
        plt.title("Chicago AirBnB versus Average Cost per Represented Zip Code")
        plt.xlabel("# of AirBnB associated with Zip Code")
        plt.ylabel("Average Cost ($US) of housing for Zip Code")
        plt.savefig("Chicago_Plot.png")


    def api_call(self, zipcode):
        self.api_key = "AIzaSyCn9PiMv32axsl4V6yjjcdaDbLrPSMKpxM"
        self.url = "https://maps.googleapis.com/maps/api/geocode/json"
        zipcode = str(zipcode)
        params = {
            'address': zipcode,
            'key': self.api_key
        }
        response = requests.get(self.url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                location = data["results"][0]["geometry"]["location"]
                lat = location["lat"]
                lng = location["lng"]
                return lat, lng
            else:
                print(f"No results found for {zipcode}")
                return None, None
        else:
            print(f"Error: {response.status_code}")
            return None, None
        
    def get_dist(self, lat1, lng1, lat2, lng2):
        lat = pow(abs(lat2-lat1), 2)
        lng = pow(abs(lng2-lng1), 2)
        return pow(lat+lng, 0.5)     

    def test_loc(self, df, i, j):
        var = df.iloc[i, j]
        print(f"Accessed: {var} at {i}, {j}")

    def test_plot(self):
        res = [[0 for _ in range(2)] for _ in range(5)]
        for i in range(len(res)):
            res[i][0] = i
            res[i][1] = i*i
        results = np.zeros((len(res), 2))
        for i in range(len(res)):
            results[i][0] = res[i][0]
            results[i][1] = res[i][1]
        xpoints = results[:, 0]
        ypoints = results[:, 1]
        print(xpoints)
        print(ypoints)
        plt.scatter(xpoints, ypoints)
        for i, label in enumerate(xpoints):
            plt.annotate(label, (xpoints[i], ypoints[i]), xytext=(5, 5), textcoords="offset points")
        plt.xlabel("Singles")
        plt.ylabel("Squares")
        plt.title("Test Plot")
        plt.show()

geo = Geocode()