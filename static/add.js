var model = {
    href: ko.observable(""),
    description: ko.observable(""),
    tag: ko.observable(""),
    extended: ko.observable(""),
    submitLabel: ko.observable("Add"),
};

ko.computed(function() {
    if (model.href() == "") {
        return;
    }

    $.getJSON("addLink/proposedUri", {uri: model.href()}, function (data) {
        // these could arrive after the user has started typing in the fields!
        
        model.description(data.description);
        model.tag(data.tag);
        model.extended(data.extended);

        model.submitLabel(data.existed ? "Update existing" : "Add");
        
    });
    
});

ko.applyBindings(model);
