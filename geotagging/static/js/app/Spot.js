$$.Spot = Backbone.Model.extend({

    layer: undefined,

    initialize: function (options) {
        _.bindAll(this);
    },

    toOpenLayers: function (){
        return this.marker
    }
});

$$.SpotCollection = Backbone.Collection.extend({
    model: $$.Spot

});

$$.SpotView = Backbone.View.extend({
    tagName: 'div',
    className: 'spot',

    events: {},

    initialize: function(options) {
        _.bindAll(this, 'render');
        this.model.view = this;
        if ( this.model.attributes.style.externalGraphic ) {
            var w = this.model.attributes.style.graphicWidth ? this.model.attributes.style.graphicWidth : 21;
            var h = this.model.attributes.style.graphicHeight ? this.model.attributes.style.graphicHeight : 25;
            var size = new OpenLayers.Size(w,h), 
                offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
            this.icon = new OpenLayers.Icon(this.model.attributes.style.externalGraphic, 
                                            size, offset);
        }

    },

    getIcon: function(){
        return this.icon ? this.icon : this.model.layer.getIcon();
    },

    render: function () {
        this.marker = new OpenLayers.Marker(
            new OpenLayers.LonLat(this.model.get('lng'), this.model.get('lat')), 
            this.getIcon().clone());
        this.model.layer.toOpenLayers().addMarker(this.marker);
        return this;
    }

});


$$.Layer = Backbone.Model.extend({
    
    map: undefined,

    getIcon: function() {
        return this.icon;
    },
    
    initialize: function (options) {
        log('init:layer');
        _.bindAll(this);
        
        this.collection = options.collection ? options.collection : new $$.SpotCollection();
        this.icon = options.icon ? options.icon : 'http://www.openlayers.org/dev/img/marker.png';
        
        /*
         * setup layer icon
         */
        var size = new OpenLayers.Size(21,25),
            offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
        
        this.icon = new OpenLayers.Icon(this.icon, size, offset);
    },
    
    toOpenLayers: function (){
        return this.view.layer
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
            view.render()
        }, this);

        
        // Add layer to map
        this.model.get('map').addLayer(this.layer);

        // TODO: remove this
        //this.model.get('map').addControl(new OpenLayers.Control.LayerSwitcher());
        
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