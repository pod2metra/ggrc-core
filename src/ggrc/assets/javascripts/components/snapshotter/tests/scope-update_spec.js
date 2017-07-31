/*!
  Copyright (C) 2017 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

describe('GGRC.Components.SnapshotScopeUpdater', function () {
  'use strict';

  var updaterViewModel;
  var containerVM;
  var originalHtml;

  beforeAll(function () {
    originalHtml = document.body.innerHTML;
  });

  afterAll(function () {
    document.body.innerHTML = originalHtml;
  });

  beforeEach(function () {
    updaterViewModel = GGRC.Components.getViewModel('SnapshotScopeUpdater');
    document.body.innerHTML =
      '<tree-widget-container></tree-widget-container>' +
      '<tree-widget-container></tree-widget-container>';
    containerVM = {
      setRefreshFlag: jasmine.createSpy('setRefreshFlag'),
      display: jasmine.createSpy('display'),
      model: {
        model_singular: 'Control'
      }
    };
    _.extend(updaterViewModel, {
      instance: new can.Map({
        title: 'TITLE',
        refresh: jasmine
          .createSpy('refresh'),
        save: jasmine.createSpy('save')
      })
    });
    spyOn($.prototype, 'viewModel').and.returnValue(containerVM);
  });

  describe('upsertIt() method', function () {
    var method;

    beforeEach(function () {
      method = updaterViewModel.upsertIt.bind(updaterViewModel);
      spyOn(GGRC.Controllers.Modals, 'confirm').and.callThrough();
    });

    describe('calls confirm method', function () {
      it('one time', function () {
        method(updaterViewModel);

        expect(GGRC.Controllers.Modals.confirm).toHaveBeenCalled();
      });

      it('with given params', function () {
        method(updaterViewModel);

        expect(GGRC.Controllers.Modals.confirm.calls.argsFor(0)).toEqual([
          jasmine.objectContaining({
            instance: updaterViewModel.instance,
            button_view: GGRC.Controllers.Modals.BUTTON_VIEW_OK_CLOSE,
            skip_refresh: true
          }),
          jasmine.any(Function),
          jasmine.any(Function)
        ]);
      });
    });
  });

  describe('_refreshContainers() method', function () {
    var method;
    var refreshDfd;

    beforeEach(function () {
      method = updaterViewModel._refreshContainers.bind(updaterViewModel);
      refreshDfd = new $.Deferred().resolve();
      spyOn(GGRC.Utils.CurrentPage, 'refreshCounts').and.returnValue(refreshDfd);
    });

    it('refreshes all page counters', function (done) {
      var result = method();
      result.then(
        function () {
          expect(GGRC.Utils.CurrentPage.refreshCounts).toHaveBeenCalled();
          done();
        }
      );
    });

    it('sets refresh flag for each tree-widget-container that contains' +
    ' snapshots', function () {
      method();

      $('tree-widget-container').each(function () {
        var viewModel = $(this).viewModel();
        expect(viewModel.setRefreshFlag).toHaveBeenCalledWith(true);
      });
    });

    it('does not set refresh flag for each tree-widget-container that does ' +
    'not contain snapshots', function () {
      _.extend(containerVM.model, {model_singular: 'Something'});
      method();
      $('tree-widget-container').each(function () {
        var viewModel = $(this).viewModel();
        expect(viewModel.setRefreshFlag).not.toHaveBeenCalled();
      });
    });
  });

  describe('_success() method', function () {
    var method;
    var refreshDfd;

    beforeEach(function () {
      method = updaterViewModel._success.bind(updaterViewModel);
      refreshDfd = new $.Deferred();
      updaterViewModel.instance.refresh.and.returnValue(refreshDfd);
      spyOn(updaterViewModel, '_showSuccessMsg');
      spyOn(updaterViewModel, '_showProgressWindow');
    });

    it('refreshes the instance attached to the component', function () {
      method();
      expect(updaterViewModel.instance.refresh).toHaveBeenCalled();
    });

    describe('after instance refresh', function () {
      it('saves the instance attached to the component', function () {
        method();
        refreshDfd.resolve();
        expect(updaterViewModel.instance.save).toHaveBeenCalled();
      });

      it('sets snapshots attr for the instance', function () {
        var expectedResult = {
          operation: 'upsert'
        };
        var wrongValue = {
          operation: 'wrongValue'
        };
        updaterViewModel.instance.attr('snapshots', wrongValue);
        method();
        refreshDfd.resolve();
        expect(updaterViewModel.instance.attr('snapshots'))
          .toEqual(
            jasmine.objectContaining(expectedResult)
          );
      });

      it('shows progress message',
        function () {
          method();
          refreshDfd.resolve();
          expect(updaterViewModel._showProgressWindow).toHaveBeenCalled();
        });

      it('shows success message',
        function () {
          method();
          refreshDfd.resolve();
          expect(updaterViewModel._showSuccessMsg).toHaveBeenCalled();
        });
    });
  });
});
