#####################       Edge Impulse Bounding Annotation import utility         #############
#                                                                                               #        
#   Use this file to update bounding box info in Edge Impulse Studio from PASCAL VOC annotated  #
#   training set.                                                                               #    
#                                                                                               #        
#   Written by Peter Ing                                                                        #
#   April 2021                                                                                  #
#                                                                                               #        
#                                                                                               #
################################# Enter your info below #########################################


# Project ID is found in project Url in EI Studio
project_id='26339' 

# API key is found under keys in studio 
api_key = 'ei_d6a8fb1a4b9f4a2dcded6f306edd802ec4a2e571d797bf67905387c996c1a88c'

# Dataset size
train_imageset_size = 33 # insert the number of training images displayed in EI Studio
test_imageset_size =  9  # insert the number of test images displayed in EI Studio

imagefiletype = 'jpg'   # specify image filetype extension

# Relative path to this file ( ideally place this file in folder that contains image data and 
# training data located in folders called "images" and "labels respectively")
path_images='./images/'
path_labels='./labels/'


###############################################################################################




#################3## Edge Impulse API endpoints ################################################

ei_list_samples_url = "https://studio.edgeimpulse.com/v1/api/" + project_id + "/raw-data"
ei_set_boundingboxes_url = "https://studio.edgeimpulse.com/v1/api/" + project_id + "/raw-data/"


################################################################################################
import requests
import json
import xml.etree.ElementTree as ET

data_collected_size = train_imageset_size + test_imageset_size

def parseVOC(filename):
    filename = path_labels + filename[:-3]+'xml'
    xmldata = ET.parse(filename)
    xmlroot = xmldata.getroot()
    label = xmlroot.find('object/name').text
    x = int(xmlroot.find('object/bndbox/xmin').text)
    y = int(xmlroot.find('object/bndbox/ymin').text)
    width = int(xmlroot.find('object/bndbox/xmax').text) - x
    height = int(xmlroot.find('object/bndbox/ymax').text) - y 

    return label, x , y , width, height


# get sampleID's

querystring = {"category":"training", "limit":data_collected_size}

headers = {"Accept": "application/json", "x-api-key": api_key }

response = requests.request("GET", ei_list_samples_url, headers=headers, params=querystring)


ei_samples = json.loads(response.text)


try:
    for i in ei_samples["samples"]:
        filenamelen =  i["filename"].find(imagefiletype) + len(imagefiletype)
        filename = i["filename"][:filenamelen]
        bndbox = parseVOC(filename)
        ei_api = ei_set_boundingboxes_url + str(i["id"]) + "/bounding-boxes"
        payload = {"boundingBoxes": [
            {
                "label": bndbox[0],
                "x": bndbox[1],
                "y": bndbox[2],
                "width": bndbox[3],
                "height": bndbox[4]
            }
        ]}
        
        headers = {
        "Accept": "application/json", "Content-Type": "application/json", "x-api-key": api_key
        }
        print("Updating bounding box for SampleID: " + str(i["id"]))
        response = requests.request("POST", ei_api, json=payload, headers=headers)
        if json.loads(response.text)["success"] == True:
            print("Connection Successfull")
        elif json.loads(response.text)["success"] == False:
            print('ERR:' + json.loads(response.text)["error"]) 
except: 
    print("ERR Check API Key and Project ID's are correct")
    

print("Done please return to Edge Impulse Studio")



