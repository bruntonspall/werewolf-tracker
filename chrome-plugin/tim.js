/*
    == Tim ==
    A tiny JavaScript micro-templating script.
    http://gist.github.com/521352

    You can use Tim to write simple templates that use JavaScript's
    familiar dot notation to replace template tags with JSON object
    properties.
    
    
    == Why is micro-templating useful? ==
    Don't you just hate writing HTML with string concatenation in
    JavaScript?
    
        "<ul class='" + myClass + "'>" + "<li id='" [...]
        
    Yuck. Now there's no need. Simply prepare an object with the
    relevant properties and keep the HTML in a micro-template. See
    below for details on keeping micro-templates inline in an HTML
    document.
    

    == How is it different from other micro-templating scripts? ==
    It is safe and secure: it doesn't use eval or (new Function), so
    it cannot execute malicious code. As such, it can be used in
    secure widgets and apps that disallow eval - e.g. Adobe Air
    sandboxes, AdSafe ads, etc.
    
    It's stripped down basic, and gives you simple templating with
    minimal fuss.

    It's just 191 bytes when minified and gzipped.
    Now in use in Sqwidget: http://github.com/premasagar/sqwidget

    
    == Usage ==
    var template = "Hello {{place}}. My name is {{person.name}}.",
        data = {
            place: "Brighton",
            person: {
                name: "Prem"
            }
        };
        
    var myText = tim(template, data);
    // "Hello Brighton. My name is Prem."


    == Using arrays ==
    The data can be, or can include, an array. Use dot notation to access
    array elements.

    E.g:
        tim(
            "Hello {{0}}",
            ["world"]
        );
        // "Hello world"
        
    Or:
        tim(
            "Hello {{places.0}}",
            {
                places: ["world"]
            }
        );
        // "Hello world"


    == Changing the {{delimter}} ==
    By default, a template tag is delimited by "{{" and "}}".
    To change this, edit the 'starts' and 'ends' vars below.
    
    
    == Embedding templates in an HTML document ==
    A really handy pattern is to include micro-templates within script
    elements that have a proprietary `type` attribute. The browser will
    not attempt to parse the scripts, because it will not recognise the
    type. You can then grab the contents of the element and use it as a
    string for the Tim script.
    
    e.g, in the HTML document:
    
        <script type="text/template" id="mytemplate">
            Hello {{place}}. My name is {{person.name}}.
        </script>
        
        
    and in the JavaScript:
    
        var template = document.getElementById("mytemplate").innerHTML,
            data = {
                place: "Brighton",
                person: {
                    name: "Prem"
                }
            };
            
        var myText = tim(template, data);
        // "Hello Brighton. My name is Prem."

*/

"use strict";

var tim = (function(){
    var starts  = "{{",
        ends    = "}}",
        path    = "[a-z0-9_][\\.a-z0-9_]*", // e.g. config.person.name
        pattern = new RegExp(starts + "("+ path +")" + ends, "gim"),
        undef;
    
    return function(template, data){
        return template.replace(pattern, function(tag, ref){
            var path = ref.split("."),
                len = path.length,
                lookup = data,
                i = 0;

            for (; i < len; i++){
                if (lookup === undef){
                    break;
                }
                lookup = lookup[path[i]];
                
                if (i === len - 1){
                    return lookup;
                }
            }
        });
    };
}());