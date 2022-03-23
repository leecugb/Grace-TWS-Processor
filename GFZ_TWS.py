import netCDF4 as nc
from osgeo import gdal, osr, ogr
import numpy as np
import sys, string, os, re
from datetime import datetime, timedelta
import tempfile
import matplotlib.pyplot as plt
from ftplib import FTP           

class Reader:
    def __init__(self,rootDir):
        self.__init_data(rootDir)
    
    
    def update(self,rootDir):
        ftp=FTP()
        ftp.connect('isdcftp.gfz-potsdam.de',21)
        ftp.voidcmd('TYPE I')
        ftp.login()
        ftp.cwd('grace/GravIS/GFZ/Level-3/TWS')
        for file in ftp.nlst():
            if re.match(r'GRAVIS.*?\.nc',file):
                os.system('wget '+'ftp://isdcftp.gfz-potsdam.de/grace/GravIS/GFZ/Level-3/TWS/'+file+' -t 0 -O '+os.path.join(rootDir,file))
        
    
    
    def __init_data(self, rootDir):
        start=datetime(2002,4,18,0,0,0)
        self.tws = np.array([])
        self.time = np.array([])
        for file in os.listdir(rootDir):
            if re.match(r'^GRAVIS.*?GFZ.*?\.nc$',file):
                pathname = os.path.join(rootDir, file)
                dataset = nc.Dataset(pathname)
                if self.tws.size == 0:
                    self.tws = dataset['tws'][:].data
                    self.time = np.array([start+timedelta(days=i) for i in dataset['time'][:].data])
                else:
                    self.tws = np.vstack([self.tws, dataset['tws'][:].data])
                    self.time = np.hstack([self.time, [start+timedelta(days=i) for i in dataset['time'][:].data]])
        temp=a.tws.reshape(-1,180*360)
        mask=(temp!=-9e33).all(0)
        X=np.vstack([[ (i-start).days for i in a.time],np.ones(temp.shape[0])])
        X=X.T
        self.gradient=np.zeros(180*360)*np.nan
        self.gradient[mask]=np.linalg.inv(X.T.dot(X)).dot(X.T.dot(   temp[:,mask]   ))[0]
        self.gradient=self.gradient.reshape(180,360)
        
    def save_file(self,data,filename):
        
        driver = gdal.GetDriverByName('GTiff')
        raster = driver.Create(filename, data.shape[1],data.shape[0], 1, gdal.GDT_Float32)
        raster.SetMetadataItem('AREA_OR_POINT', 'Point')
        raster.SetGeoTransform((0, 1, 0, 90, 0, -1))
        sr = osr.SpatialReference()
        sr.SetWellKnownGeogCS('WGS84')
        raster.SetProjection(sr.ExportToWkt())
        raster.GetRasterBand(1).WriteArray(  data*365      )
        raster.FlushCache()
        raster=None




    
    def plot(self,vector):
        mask=self.create_mask(vector)
        y=np.array([(lambda x:x[mask&(x!=-9e33)].mean())(np.repeat(np.repeat(tws,10,axis=0),10,axis=1)) for tws in self.tws])        
        temp=np.vstack([ self.time   ,y   ])
        temp=temp[:,np.argsort(temp[0])]
        plt.figure(figsize=(25,3))    
        plt.scatter(temp[0],temp[1],s=10)
        plt.plot(temp[0],temp[1])
        plt.grid()
        return temp
    
    
    def create_mask(self,vector,NoData_value = 0):
        vs=ogr.Open(vector)
        vs_lyr = vs.GetLayer()
        with tempfile.NamedTemporaryFile() as temp:
            ts = gdal.GetDriverByName('GTiff').Create(temp.name, 3600,1800, 1, gdal.GDT_Byte)
            ts.SetMetadataItem('AREA_OR_POINT', 'Point')
            sr = osr.SpatialReference()
            sr.SetWellKnownGeogCS('WGS84')
            ts.SetProjection(sr.ExportToWkt())
            ts.SetGeoTransform((0, 0.1, 0, 90, 0, -0.1))
            b1 = ts.GetRasterBand(1)
            b1.SetNoDataValue(NoData_value)
            gdal.RasterizeLayer(ts, [1], vs_lyr, burn_values=[100])
            mask=ts.GetRasterBand(1).ReadAsArray()
        return mask==100
