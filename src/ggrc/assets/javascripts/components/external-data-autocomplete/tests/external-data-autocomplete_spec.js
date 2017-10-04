/*
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import Component from '../external-data-autocomplete';

describe('GGRC.Components.externalDataAutocomplete', ()=> {
  let viewModel;
  beforeEach(()=> {
    viewModel = new (can.Map.extend(Component.prototype.viewModel));
  });

  describe('viewModel', ()=> {
    describe('renderResults get()', ()=> {
      describe('returns true', ()=> {
        it(`when "showResults" flag is turned on
            and "searchCriteria" length is greather than "minLength"`, ()=> {
            viewModel.attr('showResults', true);
            viewModel.attr('minLength', 2);
            viewModel.attr('searchCriteria', 'test');

            let result = viewModel.attr('renderResults');

            expect(result).toBe(true);
        });
      });

      describe('returns false', ()=> {
        it(`when "showResults" flag is turned off
            and "searchCriteria" length is greather than "minLength"`, ()=> {
            viewModel.attr('showResults', false);
            viewModel.attr('minLength', 2);
            viewModel.attr('searchCriteria', 'test');

            let result = viewModel.attr('renderResults');

            expect(result).toBe(false);
        });

        it(`when "showResults" flag is turned on
            and "searchCriteria" length is less than "minLength"`, ()=> {
            viewModel.attr('showResults', true);
            viewModel.attr('minLength', 2);
            viewModel.attr('searchCriteria', '');

            let result = viewModel.attr('renderResults');

            expect(result).toBe(false);
        });

        it(`when "showResults" flag is turned off
            and "searchCriteria" length is less than "minLength"`, ()=> {
            viewModel.attr('showResults', false);
            viewModel.attr('minLength', 2);
            viewModel.attr('searchCriteria', '');

            let result = viewModel.attr('renderResults');

            expect(result).toBe(false);
        });
      });
    });

    describe('openResults() method', ()=> {
      it('turnes on "showResults" flag', ()=> {
        viewModel.attr('showResults', false);

        viewModel.openResults();

        expect(viewModel.attr('showResults')).toBe(true);
      });
    });

    describe('closeResults() method', ()=> {
      it('turnes off "showResults" flag', ()=> {
        viewModel.attr('showResults', true);

        viewModel.closeResults();

        expect(viewModel.attr('showResults')).toBe(false);
      });
    });

    describe('setSearchCriteria() method', ()=> {
      let element = {
        val: jasmine.createSpy().and.returnValue('criteria'),
      };

      it('updates "searchCriteria" property', (done)=> {
        viewModel.attr('searchCriteria', null);

        viewModel.setSearchCriteria(element);

        setTimeout(()=> {
          expect(viewModel.attr('searchCriteria')).toBe('criteria');
          done();
        }, 500);
      });

      it('dispatches "criteriaChanged" event', (done)=> {
        spyOn(viewModel, 'dispatch');

        viewModel.setSearchCriteria(element);

        setTimeout(()=> {
          expect(viewModel.dispatch).toHaveBeenCalledWith({
            type: 'criteriaChanged',
            value: 'criteria',
          });
          done();
        }, 500);
      });
    });

    describe('onItemPicked() method', ()=> {
      let originalModels;
      let saveDfd;
      let item;
      beforeAll(()=> originalModels = CMS.Models);
      afterAll(()=> CMS.Models = originalModels);
      beforeEach(()=> {
        saveDfd = can.Deferred();
        viewModel.attr('type', 'TestType');
        CMS.Models.TestType = can.Model('TestType', {}, {
          save: jasmine.createSpy().and.returnValue(saveDfd),
        });
        item = {
          test: true,
        };
      });

      it('turns on "saving" flag', ()=> {
        viewModel.attr('saving', false);

        viewModel.onItemPicked(item);

        expect(viewModel.attr('saving')).toBe(true);
      });

      it('creates model based on type', ()=> {
        let model = viewModel.onItemPicked(item);

        expect(model instanceof CMS.Models.TestType).toBe(true);
      });

      it('creates model with empty context', ()=> {
        let model = viewModel.onItemPicked(item);

        expect(model.attr('test')).toBe(true);
        expect(model.attr('context')).toBe(null);
      });

      it('creates model with "external" flag', ()=> {
        let model = viewModel.onItemPicked(item);

        expect(model.attr('test')).toBe(true);
        expect(model.attr('external')).toBe(true);
      });

      it('dispatches event when istance was saved', ()=> {
        spyOn(viewModel, 'dispatch');

        let model = viewModel.onItemPicked(item);

        saveDfd.resolve().then(()=> {
          expect(viewModel.dispatch).toHaveBeenCalledWith({
            type: 'itemSelected',
            selectedItem: model,
          });
        });
      });

      it('turns off "saving" flag', ()=> {
        viewModel.attr('saving', true);

        viewModel.onItemPicked(item);

        saveDfd.resolve().then(()=> {
          expect(viewModel.attr('saving')).toBe(false);
        });
      });

      it('cleans search criteria if "autoClean" is turned on', ()=> {
        viewModel.attr('searchCriteria', 'someText');
        viewModel.attr('autoClean', true);

        viewModel.onItemPicked(item);

        saveDfd.resolve().then(()=> {
          expect(viewModel.attr('searchCriteria')).toBe('');
        });
      });

      it('does not clean search criteria if "autoClean" is turned on', ()=> {
        viewModel.attr('searchCriteria', 'someText');
        viewModel.attr('autoClean', false);

        viewModel.onItemPicked(item);

        saveDfd.resolve().then(()=> {
          expect(viewModel.attr('searchCriteria')).toBe('someText');
        });
      });
    });
  });
});

