# -*- coding: utf-8 -*-
"""
Interface between main/GUI and different modules
"""
import logging
import pandas as pd

class Resource_comparator:
    def __init__(self):
        self.dataframe_data = {}
    
    def add_new_dataframe(self, df_name: str, df_data: pd.DataFrame):
        self.dataframe_list.update({df_name : df_data})

    def dataframe_list(self):
        return self.dataframe_data.keys()
    
    def dataframe(self, df_name: str, logger: logging.Logger):
        try:
            return self.dataframe_data[df_name]
        except KeyError:
            logger.error("%s key not found in dataframe dictionary", df_name)
            

# class PVProject:
#     def __init__(self):
#         self.name = None
#         self.project_bd_code = None
#         self.project_ea_code = None
#         self.solardata = SolarDatabase()
#         self.string = StringSizeCalculator()
#         self.site = ProjectSite()
#         self.plant = PVPlant()
#         self.pyield = YieldCalculator()

# class SolarDatabase():
#     def __init__(self):
#         self.solargis = None
#         self.meteonorm = None
#         self.pvgis = None
#         self.nasa_power = None
#         self.nrel = None
#         self.siar = None
#         self.start_year = None
#         self.end_year = None

# class StringSizeCalculator():
#     def __init__(self):
#         self.tolerance = None

# class ProjectSite():
#     def __init__(self):
#         self.coord = {
#             "latitude" : None,
#             "longitude" : None,
#             "altitude" : None
#             }
#         self.location = {
#             "country" : None,
#             "region" : None,
#             "municipality" : None
#             }
#         self.longitude = None
#         self.altitude = None
        
# class PVPlant():
#     def __init__(self):
#         self.module = {
#             "model" : None,
#             "manufacturer" : None,
#             "voc" : None,
#             "vmpp" : None,
#             "impp" : None,
#             "isc" : None, 
#             "alpha" : None, 
#             "beta" : None, 
#             "gamma" : None, 
#             "length" : None,
#             "width" : None,
#             "cell_type" : None,
#             "cell_size" : None,
#             "module_type" : None,
#             "bifacial" : None,
#             "noct" : None,
#             "cell_number" : None,
#             "efficiency" : None,
#             "first_year_degradation" : None,
#             "yearly_degradation" : None,
#             "nominal_voltage" : None
#         }

#         self.inverter = {
#              "nominal_voltage" : None,
#              "MPPT_min" : None,
#              "MPPT_max" : None,
#              "MPPT_min_Q" : None,
#              "wake_up_threshold" : None
#             }

#         self.structure = {}
    




    

    
    