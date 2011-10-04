olwidget.gt_utils = {
    setStyle: function(feature, style){
        for(var key in style){
            feature.attributes.style[key] = style[key]
        }
        feature.layer.redraw()
    },
};

