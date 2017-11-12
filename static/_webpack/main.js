import Vue from "vue";
import VeeValidate from "vee-validate";

Vue.use(VeeValidate);

Vue.component("helfer-table", {
    template: "#table-template",
    data: function() {
        var filteredItems = this.globalItems.filter(function(item) {
            // console.log(item.freeAdmission);
            // console.log(this);
            return item.freeAdmission == this;
        }, this.freeAdmission == "true");
        return {
            // Default values
            email: "",
            label: this.labelPreset,
            foodPrivilege: true,
            above35: true,
            // Filter items
            // items:
            //     this.globalItems.filter(function(item) {
            //         return item.freeAdmission === this.freeAdmission;
            //     }) || []
            // items: this.globalItems.filter(function(item, this.freeAdmission) {
            //     return item.freeAdmission;
            // })
            items: filteredItems || []
        };
    },
    props: ["global-items", "label-preset", "free-admission", "prefix"],
    methods: {
        addItem: function() {
            this.items.push({
                email: this.email,
                label: this.label,
                freeAdmission: true,
                foodPrivilege: true,
                above35: true,
                regId: false,
                editing: false
            });
        },
        removeItem: function(index) {
            if (confirm(this.items[index].email + " löschen?")) {
                this.items.splice(index, 1);
            }
        },
        editItem: function(item) {
            console.log(item);
            item.editing = true;
        },
        cancelEdit: function(item) {
            item.editing = false;
        },
        doneEdit: function(item) {
            item.editing = false;
        }
    }
});

new Vue({
    el: "#app",
    data: {
        area: "Registrierung",
        testRoot: "true",
        items: [
            {
                regId: 1,
                email: "lukas@codethink.de",
                label: "Arbeitskreis",
                freeAdmission: true,
                foodPrivilege: true,
                above35: true,
                regId: false,
                firstname: "Lukas",
                lastname: "Hermann",
                age: 28,
                editing: false
            },
            {
                regId: null,
                email: "daniel@gilge.de",
                label: "Mitarbeiter",
                freeAdmission: true,
                foodPrivilege: true,
                above35: true,
                regId: false,
                firstname: null,
                lastname: null,
                age: null,
                editing: false
            },
            {
                regId: null,
                email: "someone@gmx.de",
                label: "Volunteer",
                freeAdmission: false,
                foodPrivilege: true,
                above35: true,
                regId: false,
                firstname: null,
                lastname: null,
                age: null,
                editing: false
            }
        ]
    }
});
