olwidget.gt_utils = {
    setStyle: function(feature, style){
        for(var key in style){
            feature.attributes.style[key] = style[key]
        }
        feature.layer.redraw()
    },
    getIdentifier: function(map_id, object_type, object_id){
        return map_id+"."+object_type+"."+object_id
    },
    getFeatureById: function(identifier){
        return olwidget.gt_features[identifier]
    },
    getFeature: function(map_id, object_type, object_id){
        return olwidget.gt_features[olwidget.gt_utils.getIdentifier(map_id, object_type, object_id)]
    },
};

