# -*- coding: utf-8 -*-
"""
Resource module
"""
import logging
import re
import requests
import pandas as pd

def read_solar_data_file(filepath: str, data_type: str, logger: logging.Logger,
            lat: str = None, lon: str = None, alt: str = None):
    if (filepath is None) or (filepath == ""):
        raise pd.errors.EmptyDataError
    try:
        if data_type == "Solargis - Monthly Averages":
            df_ma = _extract_solargis_ma(filepath)
        elif data_type == "Solargis - TMY":
            df_ma = _extract_solargis_tmy(filepath)
            df_ma = _convert_solargis_tmy_to_ma(df_ma)
        elif data_type == "Solargis - Historic":
            df_ma = _extract_solargis_hist(filepath)
            df_ma = _convert_solargis_hist_to_ma(df_ma)
        elif data_type == "Meteonorm - TMY":
            df_ma = _extract_meteonorm_tmy(filepath)
            df_ma = _convert_meteonorm_tmy_to_ma(df_ma)
        elif data_type == "PVGIS - TMY":
            df_ma = _extract_pvgis_tmy(lat, lon)
            df_ma = _convert_pvgis_tmy_to_ma(df_ma)
        return df_ma
    except FileNotFoundError as err:
        logger.error("File not found or not avaiable")
        raise FileNotFoundError from err
    except ConnectionError as err:
        logger.error("Connection when trying to access %s resource", data_type)
        raise ConnectionError from err
    except OSError as err:
        logger.error("OSError when trying to extract info from file")
        raise OSError from err
    except (KeyError,TypeError, AttributeError, ValueError) as err:
        logger.error("Incorrect format file")
        raise TypeError from err

def _extract_solargis_ma(filepath):
    columns = []
    data = []
    flag_data = 0

    with open(filepath, encoding="utf-8") as solargis_file:
        for i,row in enumerate(solargis_file.readlines()):
            if (row[0]=="#") or (i==0):
                continue
            if row.find("Month") != -1:
                flag_data = 1
                columns = row.split(";")
            elif flag_data == 1:
                data.append(row.split(";"))

    df_solargis_ma = pd.DataFrame(data=data,columns=columns)
    df_solargis_ma.set_index("Month", inplace=True)
    df_solargis_ma = df_solargis_ma.rename(columns={"GHIm":"GHI",
    "Diffm":"DHI","DNIm":"DNI","T24":"TEMP","WSm":"WS"})
    df_solargis_ma = df_solargis_ma.rename({"Jan":"January",
    "Feb":"February","Mar":"March","Apr":"April","May":"May",
    "Jun":"June","Jul":"July","Aug":"August","Sep":"September",
    "Oct":"October","Nov":"November","Dec":"December"})
    df_solargis_ma = _convert_index_months_from_number_to_name(df_solargis_ma)
    df_solargis_ma.columns = [item.strip() for item in df_solargis_ma.columns]
    df_solargis_ma = df_solargis_ma.drop(columns=["ALBm", "RHm", "PWATm",
            "PRECm", "SNOWDm", "CDDm", "HDDm"])
    df_solargis_ma.drop("Year", inplace=True)
    return df_solargis_ma

def _extract_solargis_tmy(filepath):
    columns = []
    data = []
    flag_data = 0
    year=pd.to_datetime(pd.date_range(
        start="01/01/1900 00:30", periods=8760, freq="H"),format="%d/%m/%Y %H:%M")
    with open(filepath, encoding="utf-8") as solargis_file:
        for i,row in enumerate(solargis_file.readlines()):
            if (row[0]=="#") or (i==0):
                continue
            if(row.find("Day") != -1) and (row.find("#") == -1):
                flag_data = 1
                columns = row.split(";")
            elif (row.find("#") == -1) and (flag_data == 1):
                data.append(row.split(";"))
    df_solargis_tmy = pd.DataFrame(data=data,columns=columns)
    df_solargis_tmy["Date"] = year
    df_solargis_tmy.drop(columns=["Day","Time"], inplace=True)
    df_solargis_tmy["Month"] = df_solargis_tmy.Date.dt.month
    df_solargis_tmy.set_index("Date", inplace=True)
    df_solargis_tmy = df_solargis_tmy.apply(pd.to_numeric,errors="coerce")
    return df_solargis_tmy

def _extract_solargis_hist(filepath):
    columns = []
    data = []
    flag_data = 0
    with open(filepath, encoding="utf-8") as solargis_file:
        for i,row in enumerate(solargis_file.readlines()):
            if (row[0]=="#") or (i==0):
                continue
            if(row.find("Date") != -1) and (row.find("#") == -1):
                flag_data = 1
                columns = row.split(";")
            elif (row.find("#") == -1) and (flag_data == 1):
                data.append(row.split(";"))
    df_solargis_hist = pd.DataFrame(data=data,columns=columns)
    df_solargis_hist["Date"] = df_solargis_hist[
        "Date"].astype(str) + " " + df_solargis_hist["Time"].astype(str)
    df_solargis_hist["Date"].replace("\.", "/", regex=True, inplace=True)
    df_solargis_hist["Date"] = pd.to_datetime(df_solargis_hist["Date"],format="%d/%m/%Y %H:%M")
    df_solargis_hist.drop(columns=["Time"], inplace=True)
    return df_solargis_hist

def _convert_solargis_tmy_to_ma(df_solargis_tmy):
    df_solargis_tmy = df_solargis_tmy[["Month","GHI","DIF","DNI","TEMP","WS"]
        ].groupby("Month").agg({"GHI":"sum","DIF":["sum"],"DNI":["sum"],
        "TEMP":["mean"],"WS":["mean"]})
    df_solargis_tmy.columns = list(map(''.join, df_solargis_tmy.columns.values))
    df_solargis_tmy = df_solargis_tmy.rename(columns={"GHIsum":"GHI",
        "DIFsum":"DHI","DNIsum":"DNI","TEMPmean":"TEMP",
        "WSmean":"WS","WDmean":"WD"})
    df_solargis_tmy = _convert_index_months_from_number_to_name(df_solargis_tmy)
    df_solargis_tmy[["GHI","DHI","DNI"]] = df_solargis_tmy[["GHI","DHI","DNI"]]/1000
    return df_solargis_tmy

def _convert_solargis_hist_to_ma(df_solargis_hist):
    number_months = _unique_months_data(df_solargis_hist)
    df_solargis_hist = df_solargis_hist.apply(pd.to_numeric,errors="coerce")
    df_solargis_hist.set_index("Date", inplace=True)
    df_solargis_hist = df_solargis_hist[["Month","GHI","DIF","DNI","TEMP","WS"]
        ].groupby("Month").agg({"GHI":"sum","DIF":["sum"],"DNI":["sum"],
        "TEMP":["mean"],"WS":["mean"]})
    df_solargis_hist.columns = list(map(''.join, df_solargis_hist.columns.values))
    df_solargis_hist = df_solargis_hist.rename(columns={"GHIsum":"GHI",
        "DIFsum":"DHI","DNIsum":"DNI","TEMPmean":"TEMP",
        "WSmean":"WS","WDmean":"WD"})
    df_solargis_hist = df_solargis_hist.assign(NM=number_months)
    df_solargis_hist = df_solargis_hist.apply(pd.to_numeric,errors="coerce")
    df_solargis_hist = _convert_index_months_from_number_to_name(df_solargis_hist)
    df_solargis_hist[["GHI","DHI","DNI"]] = (1/1000)*df_solargis_hist[
        ["GHI","DHI","DNI"]].div(df_solargis_hist.NM, axis=0)
    df_solargis_hist = df_solargis_hist.drop(columns="NM")
    return df_solargis_hist

def _extract_meteonorm_tmy(filepath):
    columns = []
    data = []
    flag_data = 0
    with open(filepath, encoding="utf-8") as meteonorm_file:
        for i,row in enumerate(meteonorm_file.readlines()):
            if (row[0]=="#") or (i==0):
                continue
            if row.find("Date (MM/DD/YYYY)") != -1:
                flag_data = 1
                columns = row.split(",")
            elif flag_data == 1:
                data.append(row.split(","))
    df_meteonorm_tmy = pd.DataFrame(data=data,columns=columns)
    df_meteonorm_tmy["Time (HH:MM)"] = df_meteonorm_tmy["Time (HH:MM)"].str.replace("24:00","00:00")
    df_meteonorm_tmy["Date (MM/DD/YYYY)"] = df_meteonorm_tmy[
        "Date (MM/DD/YYYY)"].astype(str) + " " + df_meteonorm_tmy["Time (HH:MM)"].astype(str)
    df_meteonorm_tmy["Date (MM/DD/YYYY)"] = pd.to_datetime(
        df_meteonorm_tmy["Date (MM/DD/YYYY)"],format="%m/%d/%Y %H:%M")
    df_meteonorm_tmy.drop(columns=["Time (HH:MM)"], inplace=True)
    df_meteonorm_tmy = df_meteonorm_tmy.rename(columns={
        "Date (MM/DD/YYYY)":"Date",
        "GHI (W/m^2)": "GHI",
        "DNI (W/m^2)":"DNI",
        "DHI (W/m^2)": "DHI",
        "Dry-bulb (C)":"TEMP",
        "Wspd (m/s)":"WS"})
    df_meteonorm_tmy.set_index("Date", inplace=True)
    df_meteonorm_tmy = df_meteonorm_tmy.apply(pd.to_numeric,errors="coerce")
    return df_meteonorm_tmy

def _convert_meteonorm_tmy_to_ma(df_meteonorm_tmy):
    df_meteonorm_tmy["Month"] = df_meteonorm_tmy.index.month
    df_meteonorm_tmy = df_meteonorm_tmy[["Month","GHI","DHI","DNI","TEMP","WS"]
        ].groupby("Month").agg({"GHI":"sum","DHI":["sum"],"DNI":["sum"],
        "TEMP":["mean"],"WS":["mean"]})
    df_meteonorm_tmy.columns = list(map(''.join, df_meteonorm_tmy.columns.values))
    df_meteonorm_tmy = df_meteonorm_tmy.rename(columns={"GHIsum":"GHI",
        "DHIsum":"DHI","DNIsum":"DNI","TEMPmean":"TEMP",
        "WSmean":"WS","WDmean":"WD"})
    df_meteonorm_tmy = _convert_index_months_from_number_to_name(df_meteonorm_tmy)
    return df_meteonorm_tmy

def _extract_pvgis_tmy(lat,lon):
    try:
        response = requests.get(
            "https://re.jrc.ec.europa.eu/api/v5_2/tmy?lat="+str(lat)+"45&lon="+
            str(lon)+"&usehorizon=1&outputformat=json")
        if response.status_code == 200:
            df_pvgis_tmy = response.json()["outputs"]["tmy_hourly"]
            df_pvgis_tmy = pd.json_normalize(df_pvgis_tmy)
            df_pvgis_tmy["time(UTC)"] = df_pvgis_tmy["time(UTC)"].str.split(":").str[0] \
                + " " + df_pvgis_tmy["time(UTC)"].str.split(":").str[1]
            df_pvgis_tmy["time(UTC)"] = pd.to_datetime(df_pvgis_tmy["time(UTC)"],format="%Y%m%d %H%M")
            df_pvgis_tmy.drop(columns=["IR(h)","RH","WD10m", "SP"], inplace=True)
            df_pvgis_tmy = df_pvgis_tmy.rename(columns={
                "time(UTC)":"Date",
                "G(h)": "GHI",
                "Gb(n)":"DNI",
                "Gd(h)": "DHI",
                "T2m":"TEMP",
                "WS10m":"WS"})
            df_pvgis_tmy.set_index("Date", inplace=True)
            df_pvgis_tmy = df_pvgis_tmy.apply(pd.to_numeric,errors="coerce")
            return df_pvgis_tmy
        else:
            raise ConnectionError
    except (OSError, ConnectionError) as err:
        raise ConnectionError from err

def _convert_pvgis_tmy_to_ma(df_pvgis_tmy_to_ma):
    df_pvgis_tmy_to_ma["Month"] = df_pvgis_tmy_to_ma.index.month
    df_pvgis_tmy_to_ma = df_pvgis_tmy_to_ma[["Month","GHI","DHI","DNI","TEMP","WS"]
        ].groupby("Month").agg({"GHI":"sum","DHI":["sum"],"DNI":["sum"],
        "TEMP":["mean"],"WS":["mean"]})
    df_pvgis_tmy_to_ma.columns = list(map(''.join, df_pvgis_tmy_to_ma.columns.values))
    df_pvgis_tmy_to_ma = df_pvgis_tmy_to_ma.rename(columns={"GHIsum":"GHI",
        "DHIsum":"DHI","DNIsum":"DNI","TEMPmean":"TEMP",
        "WSmean":"WS","WDmean":"WD"})
    df_pvgis_tmy_to_ma[["GHI","DHI","DNI"]] = (1/1000)*df_pvgis_tmy_to_ma[
        ["GHI","DHI","DNI"]]
    df_pvgis_tmy_to_ma = _convert_index_months_from_number_to_name(df_pvgis_tmy_to_ma)
    return df_pvgis_tmy_to_ma

def _unique_months_data(df_data: pd.DataFrame):
    df_data["Month"] = df_data.Date.dt.month
    df_data["Year"] = df_data.Date.dt.year
    df_data["MY"] = df_data["Month"].astype(str) + "_" +  df_data["Year"].astype(str)
    MY = df_data["MY"].unique()
    number_months = []
    for i in range(1,13):
        number_months.append(len([item for item in MY if re.match(str(i)+"_.",item)]))
    return number_months

def _convert_index_months_from_number_to_name(df_data):
    return df_data.rename({
        1 : "January", 2 : "February", 3 : "March", 4 : "April",
        5 : "May", 6 : "June", 7 : "July", 8 : "August",
        9 : "September", 10 : "October", 11 : "November", 12 : "December"})
