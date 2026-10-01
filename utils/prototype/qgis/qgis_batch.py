from qgis.core import QgsRectangle
from qgis.PyQt.QtCore import QSize
import os

# Yes, freeze on processed all.. but... 
# Это лучше чем уход в буффер (qgis завис - жди - это значит работает) 
# Если слишком долго, просто вбей меньше bbox или сделай размер тайла меньше 

output_dir = "C:/Users/Public/"
CUSTOM_REGION = QgsRectangle(-5498890.494254, 1678939.263413, 5238521.258036, 6946867.384204)
WIDTH_TILE = 2900
TILE_DIVISION = 3

# if white\not render title - desize\upsize WIDTH_TILE 
# and set [True,col,row]
TARGET_TILE = [False,0,1] 

get_height = lambda w, ext: int(w * (ext.height() / ext.width()))
tile_geo_width = CUSTOM_REGION.width() / TILE_DIVISION
tile_geo_height = CUSTOM_REGION.height() / TILE_DIVISION

if TARGET_TILE[0] == True:
    y = TARGET_TILE[1]
    x = TARGET_TILE[2]
    
    x_min = CUSTOM_REGION.xMinimum() + (x * tile_geo_width)
    x_max = x_min + tile_geo_width
    y_max = CUSTOM_REGION.yMaximum() - (y * tile_geo_height)
    y_min = y_max - tile_geo_height
    
    tile_extent = QgsRectangle(x_min, y_min, x_max, y_max)
    tile_h = get_height(WIDTH_TILE, tile_extent)
    
    settings = iface.mapCanvas().mapSettings()
    settings.setExtent(tile_extent)
    settings.setOutputSize(QSize(WIDTH_TILE, tile_h))
    
    job = QgsMapRendererSequentialJob(settings)
    job.start()
    job.waitForFinished() 
        
    file_name = "tile_{}_{}.png".format(y, x)
    file_path = os.path.join(output_dir, file_name)
    job.renderedImage().save(file_path, "PNG")
    print("target tile recorded: {}".format(file_name))
    exit() 


for x in range(TILE_DIVISION):
    for y in range(TILE_DIVISION):
        x_min = CUSTOM_REGION.xMinimum() + (x * tile_geo_width)
        x_max = x_min + tile_geo_width

        y_max = CUSTOM_REGION.yMaximum() - (y * tile_geo_height)
        y_min = y_max - tile_geo_height
        
        tile_extent = QgsRectangle(x_min, y_min, x_max, y_max)
        tile_h = get_height(WIDTH_TILE, tile_extent)
        
        settings = iface.mapCanvas().mapSettings()
        settings.setExtent(tile_extent)
        settings.setOutputSize(QSize(WIDTH_TILE, tile_h))
        
        job = QgsMapRendererSequentialJob(settings)
        job.start()
        job.waitForFinished()
        
        file_name = "tile_{}_{}.png".format(y,x)
        file_path = os.path.join(output_dir, file_name)
        job.renderedImage().save(file_path, "PNG")

print("Sucess {}".format(output_dir))
