/*!
    Copyright (C) 2017 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

(function (can, GGRCQ) {
  'use strict';

  GGRC.Components('questionsLink', {
    tag: 'questions-link',
    template: can.view(
      GGRC.mustache_path +
      '/components/questions-link/questions-link.mustache'
    ),
    viewModel: {
      define: {
        hasQuestions: {
          type: Boolean,
          get: function () {
            var instance = this.attr('instance');
            return GGRCQ.hasQuestions(instance.class.title_singular);
          }
        },
        questionsUrl: {
          type: String,
          get: function () {
            var instance = this.attr('instance');
            return GGRCQ.getQuestionsUrl(instance);
          }
        }
      },
      instance: null
    }
  });
})(window.can, window.GGRC.Utils.GGRCQ);
