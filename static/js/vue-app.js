/* Set up Axios
 **********************/
axios.defaults.headers = { "X-Requested-With": "XMLHttpRequest" };
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

/* Vue.js
 **********************/

Vue.use(VeeValidate, {
    locale: "de",
    dictionary: {
        de: {
            messages: {
                email: "Muss eine gültige E-Mail-Adresse sein.",
                required: "Muss eine gültige E-Mail-Adresse sein."
            }
        }
    }
});

Vue.component("helfer-table", {
    template: "#table-template",
    data: function() {
        return {
            // Default values
            email: "",
            label: this.labelPreset,
            foodPrivilege: true,
            above35: true,
            axiosBusy: false,
            axiosError: "",
            itemOldState: {}
        };
    },
    computed: {
        // a computed getter
        filteredItems: function() {
            return this.items.filter(function(item) {
                return item.freeAdmission == this;
            }, this.freeAdmission == "true");
        },
        prefix: function() {
            return this.freeAdmission == "true" ? "frei" : "zahlt";
        }
    },
    props: ["items", "area", "label-preset", "free-admission"],
    methods: {
        addItem: function() {
            var component = this;
            this.$validator.validateAll().then(function(result) {
                if (result) {
                    var item = {
                        email: component.email,
                        label: component.label,
                        area: component.area,
                        freeAdmission: component.freeAdmission === "true",
                        foodPrivilege: true,
                        above35: true
                    };
                    component.axiosError = "";
                    component.axiosBusy = true;
                    axios
                        .post("/helpers/", camelToSnake(item))
                        .then(function(response) {
                            component.axiosBusy = false;
                            item.editing = false;
                            item.regId = false;
                            item.url = response.data.url;
                            component.items.push(item);
                            component.email = ""; // empty field
                        })
                        .catch(function(error) {
                            component.axiosBusy = false;
                            component.axiosError = error.response.data.pop();
                        });
                }
            });
        },
        removeItem: function(index) {
            var item = this.items[index];
            var component = this;
            if (confirm(item.email + " löschen?")) {
                this.axiosError = "";
                this.axiosBusy = true;
                axios
                    .delete(item.url)
                    .then(function(response) {
                        component.axiosBusy = false;
                        component.items.splice(index, 1);
                    })
                    .catch(function(error) {
                        component.axiosBusy = false;
                        if (error.response) {
                            component.axiosError = error.response.data.pop();
                        }
                    });
            }
        },
        editItem: function(item) {
            Object.assign(this.itemOldState, item);
            item.editing = true;
        },
        cancelEdit: function(item) {
            item.editing = false;
        },
        doneEdit: function(item) {
            var component = this;
            this.axiosError = "";
            this.axiosBusy = true;
            axios
                .patch(item.url, camelToSnake(item))
                .then(function(response) {
                    component.axiosBusy = false;
                    item.editing = false;
                })
                .catch(function(error) {
                    console.log(error);
                    component.axiosBusy = false;
                    if (error.response) {
                        component.axiosError = error.response.data.pop();
                        Object.assign(item, component.itemOldState);
                    }
                });
        }
    }
});

var app = new Vue({
    el: "#app",
    data: {
        area: "Registrierung",
        testRoot: "true",
        items: []
    },
    mounted() {
        axios
            .get("/helpers/")
            .then(function(response) {
                var items = snakeToCamel(response.data);
                items.forEach(function(obj) {
                    obj.editing = false;
                });
                this.app.items = snakeToCamel(items);
                this.app.area = items[0].area;
            })
            .catch(function(error) {
                console.log(error);
            });
    }
});

/* Helper Functions
 **********************/

//Cookie:sessionid=7vbxih5nlwpgqxcwdndg5zk11n6pdy15; csrftoken=wJtZEH1wRQUzJC5k9VJbzk7Cl0vRqNflPS9bnMWb7o9bJQgPkYwvkbV9r52Cdh7m
//Cookie:sessionid=7vbxih5nlwpgqxcwdndg5zk11n6pdy15; csrftoken=wJtZEH1wRQUzJC5k9VJbzk7Cl0vRqNflPS9bnMWb7o9bJQgPkYwvkbV9r52Cdh7m

// Test
// var object = { snake_case_index: "test value", camelCaseIndex: "test value" };
// console.log(manipulateCase(object, "camel"));
// var obj = {
//     email: "abc@gmail.com",
//     label: "Some Nice Label",
//     area: "TEST",
//     freeAdmission: true,
//     foodPrivilege: true,
//     above35: true
// };
// axios.post("/helpers/", camelToSnake(obj)).then(function(response) {
//     console.log(response);
// });

function snakeToCamel(input) {
    return manipulateCase(input, "camel");
}
function camelToSnake(input) {
    return manipulateCase(input, "snake");
}
function manipulateCase(input, to) {
    if (input instanceof Array) {
        var newArr = [];
        input.forEach(function(obj, i) {
            newArr[i] = manipulateCase(obj, to);
        });
        return newArr;
    } else if (input instanceof Object) {
        var newObj = {};
        _.forIn(input, function(value, key) {
            switch (to) {
                case "camel":
                    newObj[_.camelCase(key)] = value;
                    break;
                case "snake":
                    newObj[_.snakeCase(key)] = value;
                    break;
            }
        });
        return newObj;
    }
}
