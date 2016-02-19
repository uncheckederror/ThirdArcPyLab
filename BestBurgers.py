#By Thomas Ryan for Geog 458
#2/19/2016
#This project is significant because it creates shapefile and geojson representations of zagat's ten best burgers in Seattle web list.
#I faced a number of different challenges the big one was understand how to parse information from the HTML data. This was different from what we did in the scraper lab. I am now very well versed in the BeautifulSoup documentation.
#Then I struggled with writing my data to a CSV. Getting the headers setup correctly and then writing to all of the cell in a row rather than just the first cell was troublesome.
#The process of creating a shapefile and geojson file from my parsed HTML data was rather convoluted. 
#I did not collaborate with anyone on this project.
#I spent about eight hours on this assignment. 4 on working with BeautifulSoup and selectors, 2 on the CSV, and 2 on the rest.

#Library imports
from bs4 import BeautifulSoup
from urllib2 import urlopen
import csv
import os
import sys
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.3\\bin')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.3\\arcpy')
sys.path.append('C:\\Program Files (x86)\\ArcGIS\\Desktop10.3\\ArcToolbox\\Scripts')
import arcpy
arcpy.env.overwriteOutput = True

#Scraping output lists
locationlinks = []
latandlong = []
latitude = []
longitude = []
BurgerPlaces = []
formattedtext = []

#Shapefile to GeoJSON conversion
from subprocess import call
os.environ["GDAL_DATA"] = "C:\\OSGeo4W\\share\\gdal"
os.environ["GDAL_DRIVER_PATH"] = "C:\\OSGeo4W\\bin\\gdalplugins"
os.environ["PROJ_LIB"] = "C:\\OSGeo4W\\share\\proj"
os.environ["PATH"] = "C:\\OSGeo4W\\bin;"+os.environ["PATH"]+";C:\\OSGeo4W\\apps\\msys\\bin;C:\\OSGeo4W\\apps\\Python27\\Scripts"

#Start scraping
base_url = ("https://www.zagat.com/l/seattle/seattles-10-best-burgers")
soup = BeautifulSoup(urlopen(base_url).read(), "lxml")

for line in soup("a"):
    container = []
    container.append(str(line.get('href')))
    for i in container:
        if "maps.google.com" in i:
            locationlinks.append(i)
       
for i in locationlinks:
    print "Location link: " + i   
    
mapString = ""
for line in soup("img"):
    container = []
    container.append(str(line.get('src')))
    for i in container:
        if "maps" in i:
            mapString = i

print "Map String: " + mapString  

maplist = mapString.split("&")

for i in maplist:
    if "markers=" in i:
        j = i.split("=")
        latandlong.append(j[1])

print latandlong

for i in latandlong:
    print i
    j = i.split(',')
    latitude.append(j[0])
    longitude.append(j[1])

print latitude
print longitude

print soup("a", class_="mobile-title")

for text in soup("a", class_="mobile-title"):
    BurgerPlaces.append(text.get_text())

print BurgerPlaces
num = 0
for i in BurgerPlaces:
    print str(i) + ": " + str(latitude[num]) + ", " + str(longitude[num])
    num = num + 1
    
count = 0
for place in BurgerPlaces:
    item = []
    item.append(BurgerPlaces[count])
    item.append(latitude[count])
    item.append(longitude[count])
    item.append(locationlinks[count])
    formattedtext.append(item)
    count = count +1

#Write to CSV
f = open("C:\\Users\\tomaryan\\Desktop\\BestBurgers.csv", "w")
fieldnames = ["name", "latitude", "longitude", "link"]
csv.writer(f, lineterminator='\n').writerow(fieldnames)

for i in formattedtext:
    csv.writer(f, lineterminator='\n').writerow(i)
    count = count + 1
        
f.close()

print "Done writing to CSV"

#Start arcpy
spRef = arcpy.SpatialReference("WGS 1984") 
arcpy.CreateFileGDB_management("C:\\Users\\tomaryan\\Desktop\\", "BestBurgers.gdb")
arcpy.TableToTable_conversion("C:\\Users\\tomaryan\\Desktop\\BestBurgers.csv", "C:\\Users\\tomaryan\\Desktop\\BestBurgers.gdb", "BestBurgers")
print "Converted to gdb layer."

curlyr = arcpy.MakeXYEventLayer_management("C:\\Users\\tomaryan\\Desktop\\BestBurgers.gdb\\BestBurgers", "latitude", "longitude", "BestBurgers_points", spRef)
curlyrreal = arcpy.SaveToLayerFile_management(curlyr, "C:\\Users\\tomaryan\\Desktop\\BestBurgers_point.lyr", "ABSOLUTE")
arcpy.CopyFeatures_management("C:\\Users\\tomaryan\\Desktop\\BestBurgers_point.lyr","C:\\Users\\tomaryan\\Desktop\\BestBurgers.shp")
print "Created shapefile."

GeoJSONoutputfile = "C:\\Users\\tomaryan\\Desktop\\BestBurgers.geojson"
cur_shapefile = "C:\\Users\\tomaryan\\Desktop\\BestBurgers.shp"
call(['C:\\OSGeo4W\\bin\\ogr2ogr','-f','GeoJSON','-t_srs','WGS84','-s_srs','EPSG:26913',GeoJSONoutputfile,cur_shapefile])
print "Created geojson file."