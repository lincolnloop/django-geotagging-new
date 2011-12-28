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
    },

});

$$.MapCollection = Backbone.Collection.extend({
    model: $$.Map
});

$$.MapView = Backbone.View.extend({
    
    settings: {
        id: undefined,
        lat: 51.50121,
        lng: -0.12489,
        el: undefined,
        maxZoom: 14,
        zoomLayer: undefined,
        mapElemId: '',
        layerEl: ''
    },

    initialize: function (options) {
        _.bindAll(this, 'addOne');
        
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
        log(this.settings.mapElemId)
        this.map = new OpenLayers.Map(this.settings.mapElemId);
        // add google maps base layer
        this.map.addLayer(new OpenLayers.Layer.Google(
            "Google Streets", // the default
            {numZoomLevels: 20}
        ));

        // center the map
        this.map.setCenter(new OpenLayers.LonLat(this.settings.lng, this.settings.lat), 14);
    },

    addOne: function (layer) {
        log('MapView:addOne');
        
        layer.set({map: this.map});
        
        var view = new $$.LayerView({
            model: layer
        });
        
        this.settings.layerEl = this.settings.layerEl ? this.settings.layerEl : 
            $('#layer-placeholder-'+this.settings.id)
        this.settings.layerEl.append(view.render().el);
        
        return this;
    },

    center: function(onLayer){
        if (onLayer){
            var bounds = this.model.collection.get(onLayer).toOpenLayers().getDataExtent();
        }else{
            var bounds = undefined;
            this.model.collection.each(function(layer){
                if (_.isUndefined(bounds)){
                    bounds = layer.toOpenLayers().getDataExtent();
                }else{
                    bounds.extend(layer.toOpenLayers().getDataExtent());
                }
            });
        }
        var olMap = this.model.toOpenLayers();
        olMap.zoomToExtent(bounds);
        if ( olMap.zoom > this.settings.maxZoom ){
            olMap.zoomTo(this.settings.maxZoom);
        }
    }


});

$$.maps = new $$.MapCollection()