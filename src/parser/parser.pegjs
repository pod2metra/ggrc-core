/*
  Copyright (C) 2017 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/


start
  = _* only_order_by:only_order_by _*
    {
      return {
        expression: {},
        keys: [],
        order_by: only_order_by,
        evaluate: function(values, keys) {
          // functions evaluates the current expresion tree, with the given
          // values
          //
          // * values, Object with all the keys as in the keys array, and their
          //   coresponding values
          return true;
        }
      };
    }
  / _* or_exp:or_exp order_by:order_by _*
    {
      var keys = jQuery.unique(or_exp.keys.sort());
      delete or_exp.keys;
      return {
        expression: or_exp,
        keys: keys,
        order_by: order_by,
        evaluate: function(values, keys) {
          // functions evaluates the current expresion tree, with the given
          // values
          //
          // * values, Object with all the keys as in the keys array, and their
          //   coresponding values
          try {
            return or_exp.evaluate(values, keys);
          } catch (e) {
            return false;
          }
        }
      };
    }
  / _*
    {
      return {
        expression: {},
        keys: [],
        order_by: {
          keys: [],
          order: '',
          compare: null
        },
        evaluate: function(values, keys) {
          return true;
        }
      };
    }
  / .*
    {
      return false;
    }

order_by
  = ' ' only_order_by:only_order_by
    {
      return only_order_by;
    }
  / _*
    {
      return {
        keys: [],
        order: '',
        compare: null
      };
    }

only_order_by
  = _* 'order by'i _+ word_list:word_list order:order
    {
      return {
        keys: word_list,
        order: order,
        compare: function(val1, val2){
          for (var i=0 ; i < word_list.length; i++){
            var key = word_list[i];
            if (val1[key] !== val2[key]){
              var a = parseFloat(val1[key]) || val1[key],
                  b = parseFloat(val2[key]) || val2[key];
              return (a < b) ^ (order !== 'asc')
            }
          }
          return false;
        }
      };
    }

word_list
  = word:word ',' word_list:word_list
    {
      return [word].concat(word_list);
    }

  / word:word
    {
      return [word];
    }

order
  = _+ 'desc'i _*
    {
      return 'desc';
    }
  / _+ 'asc'i _*
    {
      return 'asc';
    }
  / _*
    {
      return 'asc';
    }


or_exp
  = left:and_exp op:OR right:or_exp
    {
      var keys = left.keys.concat(right.keys);
      delete right.keys;
      delete left.keys;
      return {
        left: left,
        op: op,
        right: right,
        keys: keys,
        evaluate: function(values) {
          return op.evaluate(left.evaluate(values), right.evaluate(values));
        }
      };
    }
  / and_exp


and_exp
  = left:simple_exp op:AND right:and_exp
    {
      var keys = left.keys.concat(right.keys);
      delete right.keys;
      delete left.keys;
      return {
        left:left,
        op: op,
        right: right,
        keys: keys,
        evaluate: function(values) {
          return op.evaluate(left.evaluate(values), right.evaluate(values));
        }
      };
    }
  / simple_exp


simple_exp
  = left:word op:OP right:word
    {
      var lleft = left.toLowerCase();
      return {
        left: lleft,
        op: op,
        right: right,
        keys: [lleft],
        evaluate: function(values){
          if (op.name != "~" && op.name != "!~" &&
              (moment(right, "M/D/YYYY", true).isValid() ||
              moment(right, "YYYY-M-D", true).isValid())) {
            right = moment(right).format("YYYY-MM-DD");
          }
          return op.evaluate(values[lleft], right);
        }
      };
    }
  / relevant_exp
  / paren_exp
  / text_exp

relevant_exp
  = _* "#" relevant:word_list "#"
    {
      return {
        object_name: relevant[0],
        op: {name: "relevant"},
        ids: relevant.slice(1),
        keys: [],
        evaluate: function(values, keys){
          return true;
        }
      };
    }

text_exp
  = _* "~" characters:.*
    {
      return {
        text: characters.join("").trim(),
        op: {name:'text_search'},
        keys: [],
        evaluate: function(values, keys){
           keys = keys || Object.keys(values);

          function comparator(a, b){
            return a.toUpperCase().indexOf(b.toUpperCase()) > -1
          }

          return keys.reduce(function(result, key){
            if (result) return result;
            if (values.hasOwnProperty(key)){
              var value = values[key];
              if (jQuery.type(value) === "string" ){
                return comparator(value, this.text);
              } else if (jQuery.type(value) === "array") {
                return value.reduce(function(result, val){
                  return result || this.evaluate(val);
                }.bind(this), false);
              } else if (jQuery.type(value) === "object"){
                return this.evaluate(value);
              }
            }
            return result;
          }.bind(this), false);
        }
      };
    }
  / _* "!~" characters:.*
    {
      return {
        text: characters.join("").trim(),
        op: {name: 'exclude_text_search'},
        keys: [],
        evaluate: function(values, keys){
           keys = keys || Object.keys(values);

          function comparator(a, b){
            return a.toUpperCase().indexOf(b.toUpperCase()) == -1
          }

          return keys.reduce(function(result, key){
            if (!result) return result;
            if (values.hasOwnProperty(key)){
              var value = values[key];
              if (jQuery.type(value) === "string" ){
                return comparator(value, this.text);
              } else if (jQuery.type(value) === "array") {
                return value.reduce(function(result, val){
                  return result || this.evaluate(val);
                }.bind(this), false);
              } else if (jQuery.type(value) === "object"){
                return this.evaluate(value);
              }
            }
            return result;
          }.bind(this), true);
        }
      };
    }

paren_exp
  = LEFT_P or_exp:or_exp RIGHT_P
    {
      return or_exp;
    }


word
  = unquoted_word
  / quoted_word


unquoted_word
  = word:unqoted_char+
    {
      return word.join('');
    }


quoted_word
  = '"' word:quoted_char* '"'
    {
      return word.join('');
    }

unqoted_char = [a-zA-Z0-9_\-./]


quoted_char
  = '\\"'
    {
      return '"';
    }
  / [^"]


AND
  = _+ 'AND'i _+
    {
      return {
        name: 'AND',
        evaluate: function(val1, val2) { return val1 && val2; }
      };
    }
  / _* '&&'   _*
    {
      return {
        name: 'AND',
        evaluate: function(val1, val2) { return val1 && val2; }
      };
    }


OR
  = _+ 'OR'i  _+
    {
      return {
        name: 'OR',
        evaluate: function(val1, val2) { return val1 || val2;}
      };
    }
  / _* '||'   _*
    {
      return {
        name: 'OR',
        evaluate: function(val1, val2) { return val1 || val2; }
      };
    }


OP
  = _* op:'=' _*
    {
      return {
        name: op,
        evaluate: function(val1, val2) {

          if (jQuery.type(val1) === "array") {
            return val1.reduce(function(result, value) {
              return result || this.evaluate(value, val2);
            }.bind(this), false);
          } else if (jQuery.type(val1) === "object") {
            return Object.keys(val1).reduce(function(result, key) {
              return result || this.evaluate(val1[key], val2);
            }.bind(this), false);
          } else if (jQuery.type(val1) === "string") {
            return val1.toUpperCase() == val2.toUpperCase();
          } else {
            return val1 == val2;
          }
        }
      };
    }
  / _* op:'!=' _*
    {
      return {
        name: op,
        evaluate: function(val1, val2) {

          if (jQuery.type(val1) === "array") {
            return val1.reduce(function(result, value) {
              return result || this.evaluate(value, val2);
            }.bind(this), false);
          } else if (jQuery.type(val1) === "object") {
            return Object.keys(val1).reduce(function(result, key) {
              return result || this.evaluate(val1[key], val2);
            }.bind(this), false);
          } else if (jQuery.type(val1) === "string") {
            return val1.toUpperCase() != val2.toUpperCase();
          } else {
            return val1 != val2;
          }
        }
      };
    }
  / _* op:'<' _*
    {
      return {
        name: op,
        evaluate: function(val1, val2) {
          return val1 < val2;
        }
      };
    }
  / _* op:'>' _*
    {
      return {
        name: op,
        evaluate: function(val1, val2) {
          return val1 > val2;
        }
      };
    }
  / _* op:'~' _*
    {
      return {
        name: op,
        evaluate: function(val1, val2) {

          if (jQuery.type(val1) === "array") {
            return val1.reduce(function(result, value) {
              return result || this.evaluate(value, val2);
            }.bind(this), false);
          } else if (jQuery.type(val1) === "object") {
            return Object.keys(val1).reduce(function(result, key) {
              return result || this.evaluate(val1[key], val2);
            }.bind(this), false);
          } else if (jQuery.type(val1) === "string") {
            return val1.toUpperCase().indexOf(val2.toUpperCase()) > -1 ;
          } else {
            return false;
          }
        }
      };
    }
  / _* op:'!~' _*
    {
      return {
        name: op,
        evaluate: function(val1, val2) {
          if (jQuery.type(val1) === "array") {
            return val1.reduce(function(result, value) {
              return result || this.evaluate(value, val2);
            }.bind(this), false);
          } else if (jQuery.type(val1) === "object") {
            return Object.keys(val1).reduce(function(result, key) {
              return result || this.evaluate(val1[key], val2);
            }.bind(this), false);
          } else if (jQuery.type(val1) === "string") {
            // the comparison is done here
            return val1.toUpperCase().indexOf(val2.toUpperCase()) == -1 ;
          } else {
            return false;
          }
        }
      };
    }
  / _* op:'is' _*
    {
      return {
        name: op,
      };
    }


LEFT_P = '(' _*

RIGHT_P = _* ')'

_ = [ \t\r\n\f]+



