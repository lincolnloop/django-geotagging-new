$$.Spot = Backbone.Model.extend({

    layer: undefined,

    initialize: function (options) {
        _.bindAll(this, 'getLatLng');
        
        return this;
    },

    toOpenLayers: function () {
        return this.view.marker;
    },
    
    getLatLng: function () {
        if (!this.latLng) {
            this.latLng = new OpenLayers.LonLat(this.get('lng'), this.get('lat'));
        }
        
        return this.latLng;
    }

});

$$.SpotCollection = Backbone.Collection.extend({
    model: $$.Spot,
    layer: undefined
});

$$.SpotView = Backbone.View.extend({
    tagName: 'div',
    className: 'spot',

    events: {},

    initialize: function (options) {
        _.bindAll(this, 'render', 'markerClick');
        this.model.view = this;
        if (this.model.attributes.style.externalGraphic) {
            var w = this.model.attributes.style.graphicWidth ? this.model.attributes.style.graphicWidth : 21;
            var h = this.model.attributes.style.graphicHeight ? this.model.attributes.style.graphicHeight : 25;
            var size = new OpenLayers.Size(w,h), 
                offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
            this.icon = new OpenLayers.Icon(this.model.attributes.style.externalGraphic, 
                                            size, offset);
        };
    },

    getIcon: function () {
        return this.icon ? this.icon : this.model.layer.getIcon();
    },

    render: function () {
        //
        // feature is used to create a marker or a popup
        //
        this.feature = new OpenLayers.Feature(this.model.layer.toOpenLayers(), this.model.getLatLng());
        
        // popup attributes
        this.feature.closeBox = true;
        this.feature.popupClass = OpenLayers.Class(OpenLayers.Popup.Anchored, {
            'autoSize': true
        });
        this.feature.data.popupContentHTML = '<h2>test</h2><p>Hello World!</p>';
        this.feature.data.overflow = "auto";
        this.feature.data.icon = this.getIcon();
        
        // create the marker
        this.marker = this.feature.createMarker();
        this.model.layer.toOpenLayers().addMarker(this.marker);
        
        this.marker.events.register("mousedown", this.feature, this.markerClick);
        
        return this;
    },
    
    markerClick: function (event) {
        log('Spot:markerClick');
        
        log(this.model.layer.get('map'));
        
        if (this.popup == null) {
            this.popup = this.feature.createPopup();
            this.model.layer.get('map').addPopup(this.popup);
            this.popup.show();
        } else {
            this.popup.toggle();
        }
        OpenLayers.Event.stop(event);
    }

});


$$.Layer = Backbone.Model.extend({
    
    map: undefined,
    
    initialize: function (options) {
        log('init:layer');
        _.bindAll(this);
        
        this.collection = options.collection ? options.collection : new $$.SpotCollection();
        this.icon = options.icon ? options.icon : 'http://www.openlayers.org/dev/img/marker.png';

        this.collection.layer = this;
        
        /*
         * setup layer icon
         */
        var size = new OpenLayers.Size(21,25),
            offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
        
        this.icon = new OpenLayers.Icon(this.icon, size, offset);
    },

    getIcon: function () {
        return this.icon;
    },
    
    toOpenLayers: function () {
        return this.view.layer;
    }
    
});

$$.LayerCollection = Backbone.Collection.extend({
    model: $$.Spot

});

$$.LayerView = Backbone.View.extend({
    tagName: 'div',
    className: 'layer',

    events: {
        'change input': 'toggleLayer'
    },

    initialize: function(options) {
        _.bindAll(this, 'render');
        
        this.model.view = this;
        this.model.collection.bind("remove", this.remove);
        this.model.collection.bind("add", this.add);
    },

    remove: function(spot){
        //This is bound to a collection
        this.layer.toOpenLayers().removeMarker(spot.toOpenLayers());
    },

    add: function(spot, collection){
        //This is bound to a collection
        spot.layer = this.layer;
        spot.view = new $$.SpotView({
            model: spot
        });
        spot.view.render();
    },

    render: function () {
        log('LayerView:render');
        /*
         * render Layer, Makers and layer display control
         */
        var template;
        
        /*
         * LAYERS
         */
        // create an marker layer
        this.layer = new OpenLayers.Layer.Markers(this.model.get('title'));
        
        // TODO: build this as a spot view or something
        // this.model.collection.each(function (spot) {
        //     var marker = new OpenLayers.Marker(new OpenLayers.LonLat(spot.get('lng'), spot.get('lat')), this.model.icon.clone());
        //     this.layer.addMarker(marker);
        // }, this);
        this.model.collection.each(function (spot) {
            spot.layer = this.model;
            var view = new $$.SpotView({
                model: spot
            });
            view.render();
        }, this);

        
        // Add layer to map
        this.model.get('map').addLayer(this.layer);
        
        /*
         * TEMPLATE
         */
        template = $.tmpl('<label><input type="checkbox" checked="checked" />${title}</label>', this.model.toJSON());
        
        //log(template);
        //log(this.model.toJSON());
        
        $(this.el).html(template);
        
        return this;
    },
    
    toggleLayer: function (event) {
        log('toggleLayer');
        var input = $(event.target),
            visible = true;
        if (!input.is(':checked')) {
            visible = false;
        }
        
        this.layer.setVisibility(visible);
        
        return this;
    }

});