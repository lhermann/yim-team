Vue.component("helfer-table", {
    template: "#table-template",
    data: function() {
        return {
            items: [
                {
                    regId: 1,
                    email: "lukas@codethink.de",
                    label: "Label",
                    editing: false,
                    firstname: "Lukas",
                    lastname: "Hermann",
                    age: 28
                },
                {
                    regId: null,
                    email: "lukas@codethink.de",
                    label: "Label",
                    editing: false,
                    firstname: null,
                    lastname: null,
                    age: null
                }
            ]
        };
    },
    props: ["email", "label", "free-admission", "food-privelege"],
    methods: {
        addItem: function() {
            this.items.push({
                email: this.email,
                label: this.label,
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

var app = new Vue({
    el: "#app",
    data: {
        area: "Registrierung"
    }
});
