/*
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

 export default {
   update: function (model, data, options) {
     var url = '/api/' + model.table_plural;
     var transform = model.toBulkModel;
     var dfd = can.Deferred();

     if (transform) {
       data = transform(data, options);
     }

     $.ajax({
       url: url,
       method: 'PATCH',
       data: JSON.stringify(data),
       contentType: 'application/json',
     }).done(function (res) {
       dfd.resolve(res);
     }).fail(function (err) {
       dfd.reject(err);
     });

     return dfd;
   }
 }
