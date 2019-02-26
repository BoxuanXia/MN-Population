###Boxuan Xia
###wrap up 2 

import arcpy
import unicodedata

##set up the workplace
theDirectory = r"e:\work2\wrap_up2"
arcpy.env.workspace = theDirectory

##name files to variable
CsvState = "nhgis0002_ds172_2010_state.csv"
CsvCounty = "nhgis0002_ds172_2010_county.csv"
US_state_2010 = "US_state_2010.shp"
US_county_2010 = "US_county_2010.shp"

##convert to dbf table
arcpy.TableToDBASE_conversion(CsvState, theDirectory)
arcpy.TableToDBASE_conversion(CsvState, theDirectory)

#name dbase file to variable
dBase_US_state = "nhgis0002_ds172_2010_state.dbf"
dBase_US_county = "nhgis0002_ds172_2010_county.dbf"

#Join Dbf table to shapefile
arcpy.JoinField_management(US_state_2010,"GISJOIN",dBase_US_state,"GISJOIN")
arcpy.JoinField_management(US_county_2010,"GISJOIN",dBase_US_county,"GISJOIN")

#create new cloumn for store population density
arcpy.AddField_management(US_state_2010, "POP_dense", "FLOAT")
arcpy.AddField_management(US_county_2010, "POP_dense", "FLOAT")


#field calculation for population density
arcpy.CalculateField_management(US_state_2010, "POP_dense", "!H7V001! /" + "(!Shape_area!/1000000)", "PYTHON", "")
arcpy.CalculateField_management(US_county_2010, "POP_dense", "!H7V001! /" + "(!Shape_area!/1000000)", "PYTHON", "")



## state has highest population density
rows = arcpy.SearchCursor(US_state_2010,
                          fields="NAME; POP_dense",
                          sort_fields="POP_dense D; NAME D")
print ("-----state have the highest population density-----")
for row in rows:
    print("State: {0}, POP_density: {1}".format(
        row.getValue("NAME"),
        row.getValue("POP_dense")))
    break

print "\n"

## county has highest pop density
rows1 = arcpy.SearchCursor(US_county_2010,
                          fields="NAME; POP_dense",
                          sort_fields="POP_dense D; NAME D")
print ("-----state have the highest population density-----")
for row in rows1:
    print("County: {0}, POP_density: {1}".format(
        row.getValue("NAME"),
        row.getValue("POP_dense")))
    break

print "\n"

## top ten pop density by county
newrows2 = arcpy.SearchCursor(US_county_2010,
                          fields="STATE; NAME; POP_dense;",
                          sort_fields="POP_dense D")
print ("-----top ten pop density by county: ------" )
count = 0 
for row in newrows2:
    if count <=9:
        count+=1
        print count, "State:{0}, County: {1}, POP_density: {2}".format(
            row.getValue("STATE"),
            (row.getValue("NAME")).encode('ascii','ignore'),
            row.getValue("POP_dense")), "per square kilometer"
    else:
        break
print "\n"

##add field for population proportion 
arcpy.AddField_management(US_county_2010, "POP_Prop", "DOUBLE")

##join the State.shp to county.shp
inFeatures = "US_county_2010.shp"
joinField = "STATE"
joinTable = "US_state_2010.shp"
fieldList = ["H7V001"]
arcpy.JoinField_management (inFeatures, joinField, joinTable, joinField, fieldList)

##add field store state pop in double format
arcpy.AddField_management(US_county_2010, "State_Sum", "DOUBLE")
##copy the value for State pop
arcpy.CalculateField_management(US_county_2010, "State_Sum","!H7V001_1!", "PYTHON", "")


##calulate proportion for each county
with arcpy.da.UpdateCursor(US_county_2010,["Pop_prop","H7V001","State_Sum"])as cursor:
    for row in cursor:
        row[0] = row[1]/row[2]*100
        cursor.updateRow(row)
        
##arcpy.CalculateField_management(US_county_2010, "POP_Prop1", "100*"+"!H7V001!/" + "!H7V001_1!", "PYTHON", "")


##ighest density county in each state
zipdata = ("STATE","NAME","Pop_prop")
zip1 = {}
with arcpy.da.SearchCursor(US_county_2010, zipdata) as cursor:
    for r in cursor:
        if r[0] in zip1:
            MaxValue = zip1[r[0]][2]
            if r[2] > MaxValue:
                zip1[r[0]]= (r[0],r[1],r[2])
        else:
            zip1[r[0]]= (r[0],r[1],r[2])
print ("-----Highest density county in each state: -----")
for key,value in zip1.items():
    print 'State: ',str(key),', County: ',str(value[1]),', POP prop: ',str(value[2]), "percents"
