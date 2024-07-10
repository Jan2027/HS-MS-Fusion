import numpy as np
from scipy import ndimage
from osgeo import gdal
import adjustNumbers
from tqdm import trange, tqdm
from scipy import ndimage



def read_geotiff(filename):
    print("Beginne Einlesen der Datei: " + str(filename))
    
    ds = gdal.Open(filename)
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    bands = []
    for i in range(1, ds.RasterCount + 1):
        bands.append(ds.GetRasterBand(i).ReadAsArray())
        
    arr = np.stack(bands, axis=0)
        
    arr = np.dstack(arr)
    
    print("Einlesen der Datei ist abgeschlossen")
    return arr, ds 

def read_envi_file(file_path):
    """
    Liest eine ENVI-Datei im BSQ-Format und gibt die Daten als Array zurück.
    """
    dataset = gdal.Open(file_path)

    if dataset is None:
        raise Exception("Konnte die Datei nicht öffnen.")

    num_bands = dataset.RasterCount
    arrays = []
    for band_idx in range(1, num_bands + 1):
        band = dataset.GetRasterBand(band_idx)
        band_array = band.ReadAsArray()
        arrays.append(band_array)

    
    arr = np.stack(arrays, axis=0)
    arr = np.dstack(arr)

    return arr, dataset

def write_envi_file(output_path, arrays, in_ds, metadata=None):
    """
    Schreibt ein Array in eine ENVI-Datei im BSQ-Format.
    """
    num_bands = len(arrays)
    height, width = arrays[0].shape

    driver = gdal.GetDriverByName('ENVI')
    output_dataset = driver.Create(output_path, width, height, num_bands, gdal.GDT_Float32)
    #output_dataset.setProjection(in_ds.GetProjection())
    output_dataset.SetGeoTransform(in_ds.GetGeoTransform())

    if metadata:
        output_dataset.SetMetadata(metadata)

    with tqdm(total=num_bands) as pbar:
        for band_idx, band_array in enumerate(arrays, start=1):
            output_band = output_dataset.GetRasterBand(band_idx)
            output_band.WriteArray(band_array)
            pbar.update(1)

    

    output_dataset = None
    
    
def sfim(lowres, hires, blurfactor=1.0):
    blurredres = ndimage.gaussian_filter(hires, blurfactor, mode="nearest")
    zoomfactor = hires.shape[0] / lowres.shape[0]

    assert zoomfactor.is_integer()
    assert zoomfactor == hires.shape[1] / lowres.shape[1]
    lowres_upscaled = ndimage.zoom(lowres, zoomfactor)
    denominator = lowres_upscaled * hires
    result = np.ones_like(hires)
    np.divide(denominator, blurredres, out=result, where=blurredres != 0)
    return result

def createLowResMS(Hires , shapeHires, shapeLowres):
    rows1, cols1, bands1 = shapeHires
    rows2, cols2, bands2 = shapeLowres
    
    low_res_ms = np.zeros((rows2, cols2, bands1))
    
    for b in range(bands1):
            tmp = ndimage.zoom(Hires[:, :, b], (rows2/rows1, cols2/cols1), order=1)
            low_res_ms[:, :, b] = tmp

    return low_res_ms


def upscale_2d_array(a, factor):
    return(np.repeat(a, factor, axis=1).repeat(factor, axis=0))

if __name__ == '__main__':
   enMapPath = PATHTOENMPA
   sentinel_file = PATHTOSENTINEL

   savePath = SAVEPATH

   data_array_envi, in_ds = read_envi_file(enMapPath)
   data_array_senti, in_ds = read_geotiff(sentinel_file)
   


   data_array_senti, data_array_envi = adjustNumbers.adjustArrays(data_array_senti, data_array_envi, 3)
   hires = data_array_senti[:,:,0]
   
   
   
   bands = data_array_envi.shape[2]
   fusionArrays = []
   
   low_res_ms = createLowResMS(data_array_senti, data_array_senti.shape, data_array_envi.shape)
   
   
   for i in trange(bands):
       HSMS = sfim(data_array_envi[:,:,i], hires, blurfactor=0)
       HSMS = HSMS.astype("float64")
       fusionArrays.append(HSMS)
       print(np.mean(HSMS))
   
   
   print(fusionArrays[0].shape)
   write_envi_file(savePath, fusionArrays, in_ds)
