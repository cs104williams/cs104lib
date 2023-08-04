
from datascience import *
import numpy as np
import pkg_resources

def check_table(t):
    if t.num_columns < 2:
        ValueError("Table must have atleast two columns")
    geo_col = t.column(0)
    if not np.issubdtype(geo_col.dtype, np.character):
        raise ValueError("The first column passed to map_table must contain strings")
    num_col = t.column(1)
    if not np.issubdtype(num_col.dtype, np.number):
        raise ValueError("The second column passed to map_table must contain numeric values")


class States(Map):
    
    _default_lat_lon = [48, -102]
    _default_zoom = 3
    
    def map_table(table, **kwargs):
        states = States.read_geojson(pkg_resources.resource_filename(__name__, 'data/us-states.json'))
        
        kws = {
            "nan_fill_color": 'gray', 
            "nan_fill_opacity": 0.2,
            "line_opacity": 0.3
        }
        
        kws.update(kwargs)

        kws.setdefault('legend_name',table.labels[1])
        t = Table().with_columns("geo", table.column(0),
                                 "values", table.column(1))
        states.color(t, **kws).show()

    def _autozoom(self):
        """Calculate zoom and location."""
        attrs = {}

        attrs['location'] = self._default_lat_lon
        attrs['zoom_start'] = self._default_zoom
        return attrs
        
class Countries(Map):
    
    def map_table(table, **kwargs):
        countries = Countries.read_geojson(pkg_resources.resource_filename(__name__, 'data/world-countries.json'))
        
        kws = {
            "nan_fill_color": 'gray', 
            "nan_fill_opacity": 0.2,
            "line_opacity": 0.3
        }
        
        kws.update(kwargs)

        check_table(table)

        kws.setdefault('legend_name',table.labels[1])

        t = Table().with_columns("geo", table.apply(lambda x: x.upper(), 0),
                                 "values", table.column(1))
        countries.color(t, **kws).show()
        
class HopkinsForest(Map):

    _default_zoom = 15
    
    def map_table(table, **kwargs):
        countries = HopkinsForest.read_geojson(pkg_resources.resource_filename(__name__, 'data/hopkins-forest.json'))
        
        kws = {
            "nan_fill_color": 'gray', 
            "nan_fill_opacity": 0.2,
            "line_opacity": 0.3
        }
        
        kws.update(kwargs)
        kws.setdefault('legend_name',table.labels[1])

        t = Table().with_columns("geo", table.column(0),
                                 "values", table.column(1))
        countries.color(t, **kws).show()
        
    def _autozoom(self):
        attrs = super()._autozoom()
        attrs['zoom_start'] += 2
        return attrs
