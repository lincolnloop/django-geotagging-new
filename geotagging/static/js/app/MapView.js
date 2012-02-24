$$.Map = Backbone.Model.extend({
    initialize: function (options) {
        _.bindAll(this);

        this.collection = options.collection ? options.collection : new $$.LayerCollection();
        
        if (_.isUndefined(options.id))
            return

        var viewOptions = {
            collection: this.collection
        }

        $.extend(viewOptions, options);
        this.view = new $$.MapView(viewOptions);
        this.view.model = this;
    },
    
    toOpenLayers: function (){
        return this.view.map
    }

});

$$.MapCollection = Backbone.Collection.extend({
    model: $$.Map
});

$$.MapView = Backbone.View.extend({
    
    initialize: function (options) {
        log('MapView:initialize');
        _.bindAll(this, 'addOne');
        
        this.settings = {
            id: undefined,
            el: undefined,
            maxZoom: 14,
            minZoom: 5,
            defaultZoom: 7,
            zoomLayer: undefined,
            mapElemId: '',
            layerEl: '',
            center: {lon:0,lat:0},
            static: false
        };

        this.collection.bind('add', this.addOne);

        /*
         * extend the default map settings w/ user's map settings
         */
        if (options) {
            $.extend(this.settings, options);
        }
        this.el = this.settings.el ? this.settings.el : $('#'+this.settings.id);
        
        // create the map instace
        //this.map = new google.maps.Map(this.el.get(0), map_options);
        this.settings.mapElemId = this.settings.mapElemId ? this.settings.mapElemId : 
            'placeholder-'+this.settings.id

        this.map = new OpenLayers.Map(this.settings.mapElemId);
        // add google maps base layer
        this.map.addLayer(new OpenLayers.Layer.Google(
            "Google Streets", // the default
            {numZoomLevels: 20}
        ));

        if (this.settings.static){
            $(this.map.controls).each(function(i, control){
                control.deactivate(); 
                this.map.removeControl(control)});
        }
    },

    addOne: function (layer) {
        log('MapView:addOne');
        
        layer.set({map: this.map});
        
        //Does this leak memory?
        var view = new $$.LayerView({
            model: layer
        });
        
        this.settings.layerEl = this.settings.layerEl ? this.settings.layerEl : 
            $('#layer-placeholder-'+this.settings.id)
        this.settings.layerEl.append(view.render().el);
        
        return this;
    },

    enumerate: function(options){
        options = options || {}
        var _this = this
        if ( options.layers ){
            options.color = options.color || 'red'
            var numbering = 1
            $(options.layers).each(function(i, layer_name){ 
                var layer = _this.collection.get(layer_name);
                var old = $(_.toArray(layer.collection).slice(0))
                old.each(function(j, spot){ 
                    var item = {id: spot.attributes.id,
                                lng: spot.attributes.lng,
                                lat: spot.attributes.lat,
                                style: {},
                                number: numbering,
                                title: spot.attributes.title};
                    item.style.externalGraphic = 'http://google-maps-icons.googlecode.com/files/'+options.color+(numbering < 10 ? "0"+numbering : numbering)+'.png';
                    item.style.graphicHeight = 27;
                    item.style.graphicWidth = 27;
                    layer.collection.add(new $$.Spot(item));
                    layer.collection.remove(spot);
                    $('.map-legend.id'+item.id).attr("class", "map-legend number"+(numbering < 10 ? "0"+numbering : numbering));
                    numbering += 1;
                });
            });
        }else if ( options.collection ){
            options.collection.each(function(i, object){
                log(object)
            });
        }
    },

    center: function(onLayer){
        var bounds;
        
        if (onLayer){
            bounds = this.model.collection.get(onLayer).toOpenLayers().getDataExtent();
        } else {
            this.model.collection.each(function(layer){
                var current_bounds = layer.toOpenLayers().getDataExtent();
                if ( current_bounds != null ){ 
                    if (_.isUndefined(bounds)) {
                        bounds = current_bounds;
                    } else {
                        bounds.extend(current_bounds);
                    }
                }
            });
        }
        var olMap = this.model.toOpenLayers();
        if ( _.isUndefined(bounds) ){
            olMap.setCenter( new OpenLayers.LonLat(this.settings.center.lon, 
                                                   this.settings.center.lat) );
            olMap.zoomTo(this.settings.defaultZoom);
        }else{
            olMap.zoomToExtent(bounds);
        }
        if (olMap.zoom > this.settings.maxZoom) {
            olMap.zoomTo(this.settings.maxZoom);
        }
        if (olMap.zoom < this.settings.minZoom) {
            olMap.zoomTo(this.settings.minZoom);
        }
    },

    remove: function(layerName){
        //This is bound to a collection
        var layer = this.collection.get(layerName);
        var old = $(_.toArray(layer.collection).slice(0))
        old.each(function(i, spot){
            layer.collection.remove(spot);
        });
    },


});

$$.maps = new $$.MapCollection();