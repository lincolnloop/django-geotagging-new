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
    },
    
    toOpenLayers: function (){
        return this.view.map
    }
    
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

        // map events
        $(document).bind('maps:center', this.centerMap);
        $(document).bind('maps:sortChange', this.sortChange);
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
    }

});

$$.maps = new $$.MapCollection()