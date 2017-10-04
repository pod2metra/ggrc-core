/*
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import Component from '../external-data-provider';

describe('GGRC.Components.externalDataProvider', ()=> {
  let viewModel;
  let events;
  beforeEach(()=> {
    viewModel = new (can.Map.extend(Component.prototype.viewModel));
    events = Component.prototype.events;
  });

  describe('init() method', ()=> {
    let method;
    beforeEach(()=> {
      method = Component.prototype.init.bind({viewModel});
    });

    it('loads data', ()=> {
      spyOn(viewModel, 'loadData');

      method();

      expect(viewModel.loadData).toHaveBeenCalled();
    });
  });

  describe('viewModel', ()=> {
    describe('loadData() method', ()=> {
      let originalConfig;
      let requestDfd;
      let $getSpy;
      beforeAll(()=> originalConfig = GGRC.config);
      afterAll(()=> GGRC.config = originalConfig);
      beforeEach(()=> {
        GGRC.config = {
          external_services: {
            Person: 'testUrl',
          },
        };
        requestDfd = $.Deferred();
        $getSpy = spyOn($, 'get');
        $getSpy.and.returnValue(requestDfd);
      });

      it('turns on "loading" flag', ()=> {
        viewModel.attr('loading', false);

        viewModel.loadData();

        expect(viewModel.attr('loading')).toBe(true);
      });

      it('increases request number', ()=> {
        viewModel.attr('currentRequest', 0);

        viewModel.loadData();

        expect(viewModel.attr('currentRequest')).toBe(1);
      });

      it('send correct request', ()=> {
        viewModel.attr('searchCriteria', 'someText');
        viewModel.attr('type', 'Person');

        viewModel.loadData();

        expect($.get).toHaveBeenCalledWith({
          url: 'testUrl',
          data: {
            prefix: 'someText',
          },
        });
      });

      it('sets response to "values" property', (done)=> {
        let testResponse = ['res1', 'res2'];
        viewModel.attr('values', null);

        viewModel.loadData();

        requestDfd.resolve(testResponse).then(()=> {
          expect(viewModel.attr('values').serialize()).toEqual(testResponse);
          done();
        });
      });

      it('shows message if there was error', (done)=> {
        spyOn(GGRC.Errors, 'notifier');
        viewModel.attr('type', 'TestModel');

        viewModel.loadData();

        requestDfd.reject().always(()=> {
          expect(GGRC.Errors.notifier)
            .toHaveBeenCalledWith('error', 'Unable to load TestModels');
          done();
        });
      });

      describe('turns off "loading" flag', ()=> {
        beforeEach(()=> {
          spyOn(GGRC.Errors, 'notifier');
          viewModel.attr('loading', true);
          viewModel.loadData();
        });

        it('when there was success', (done)=> {
          requestDfd.resolve().always(()=> {
            expect(viewModel.attr('loading')).toBe(false);
            done();
          });
        });

        it('when there was error', (done)=> {
          requestDfd.reject().always(()=> {
            expect(viewModel.attr('loading')).toBe(false);
            done();
          });
        });
      });

      it('processes callbacks only for latest request', (done)=> {
        let request1 = can.Deferred();
        let response1 = ['res1'];
        let request2 = can.Deferred();
        let response2 = ['res2'];

        $getSpy.and.returnValue(request1);
        viewModel.loadData();
        $getSpy.and.returnValue(request2);
        viewModel.loadData();

        request2.resolve(response2);
        request1.resolve(response1);

        can.when(request1, request2).then(()=> {
          expect(viewModel.attr('values').serialize()).toEqual(response2);
          done();
        });
      });
    });
  });

  describe('events', ()=> {
    describe('"{viewModel} searchCriteria" handler', ()=> {
      let handler;
      beforeEach(()=> {
        handler = events['{viewModel} searchCriteria'].bind({viewModel});
      });

      it('loads data', ()=> {
        spyOn(viewModel, 'loadData');

        handler();

        expect(viewModel.loadData).toHaveBeenCalled();
      });
    });
  });
});
