# This is a fork of Bootstrap Typeahead that adds minimal but powerful extensions.

### For example, process typeahead list asynchronously and return objects

```coffeescript
  # This example does an AJAX lookup and is in CoffeeScript
  $('.typeahead').typeahead(
    # source can be a function
    source: (typeahead, query) ->
      # this function receives the typeahead object and the query string
      $.ajax(
        url: "/lookup/?q="+query
        # i'm binding the function here using CoffeeScript syntactic sugar,
        # you can use for example Underscore's bind function instead.
        success: (data) =>
          # data must be a list of either strings or objects
          # data = [{'name': 'Joe', }, {'name': 'Henry'}, ...]
          typeahead.process(data)
      )
    # if we return objects to typeahead.process we must specify the property
    # that typeahead uses to look up the display value
    property: "name"
  )
```

### For example, process typeahead list synchronously and fire a callback on selection

```javascript
  // This example is in Javascript, collects html in some li's and returns it
  $('.typeahead').typeahead({
    source: function (typeahead, query) {
      var return_list = []
      $("li").each(function(i,v){
        return_list.push($(v).html())
      })
      // here I'm just returning a list of strings
      return return_list
    },
    // typeahead calls this function when a object is selected, and
    // passes an object or string depending on what you processed, in this case a string
    onselect: function (self) {
      alert('Selected '+self)
    }

  })
```

### and a very simple example, showing you can pass list of objects as source, and get that object via onselect
```javascript
  $('.typeahead').typeahead({
    // note that "value" is the default setting for the property option
    source: [{value: 'Charlie'}, {value: 'Gudbergur'}, ...],
    onselect: function(self) { console.log(self) }
  })
```

Note that onselect works without source as a function and vice versa. Events may be a cleaner solution to passing callbacks and using bind all over the place, but I tried to strike a balance between modifying the core source too much and adding functionality, so until further improvements on the original Typeahead source I think these additions are very helpful.

**Update 02/23/2012: Fixed a bug**

### Gudbergur Erlendsson, reach me here or gudbergur at gmail