/*
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

describe('GGRC.VM.BaseTreeItemVM', function () {
  'use strict';

  var vm;

  beforeEach(function () {
    vm = new GGRC.VM.BaseTreeItemVM();
  });

  describe('initChildTreeDisplay() method', function () {
    beforeEach(function () {
      spyOn(GGRC.Utils.TreeView, 'getModelsForSubTier')
        .and.returnValue({
          available: ['Foo', 'Bar', 'Baz'],
          selected: ['Foo'],
        });
      spyOn(GGRC.Utils.ObjectVersions, 'getWidgetConfig')
        .and.callFake(function (model) {
          return {
            widgetName: model + 'Widget',
          };
        });

      vm.attr('instance', {type: 'Type'});
    });

    it('initialised child models list', function () {
      var modelsList;
      var displayList;
      vm.initChildTreeDisplay();

      modelsList = vm.attr('selectedChildModels').serialize();
      displayList = vm.attr('childModelsList').serialize();

      expect(modelsList.length).toEqual(1);
      expect(modelsList).toEqual(['Foo']);

      expect(displayList).toEqual([
        {
          name: 'Foo',
          widgetName: 'FooWidget',
          display: true,
        }, {
          name: 'Bar',
          widgetName: 'BarWidget',
          display: false,
        }, {
          name: 'Baz',
          widgetName: 'BazWidget',
          display: false,
        },
      ]);
    });
  });

  describe('onExpand() method', function () {
    it('converts expanded property to the opposite value', function () {
      vm.attr('expanded', true);

      vm.onExpand();

      expect(vm.attr('expanded')).toBeFalsy();
    });

    it('converts expanded property to the opposite value', function () {
      vm.attr('expanded', false);

      vm.onExpand();

      expect(vm.attr('expanded')).toBeTruthy();
    });
  });

  describe('onClick() method', function () {
    beforeEach(function () {
      spyOn(vm, 'select');
    });

    describe('if instance is Person', ()=> {
      let dfd;
      beforeEach(()=> {
        vm.attr('instance', new can.Map({
          type: 'Person',
        }));
        dfd = can.Deferred();
        vm.attr('resultDfd', dfd);
      });

      it('call select() if there is result', ()=> {
        vm.attr('result', true);

        vm.onClick('element');

        expect(vm.select).toHaveBeenCalledWith('element');
      });

      it(`call waiting for deferred and call select()
          if there is no result`, (done)=> {
        vm.attr('result', false);

        vm.onClick('element');
        expect(vm.select).not.toHaveBeenCalled();

        dfd.resolve().then(()=> {
          done();
          expect(vm.select).toHaveBeenCalledWith('element');
        });
      });
    });

    describe('if instance is Cycle', ()=> {
      beforeEach(()=> {
        vm.attr('instance', new can.Map({
          type: 'Cycle',
        }));
      });

      describe('toggle "expanded" option if page is "Workflow"', ()=> {
        beforeEach(()=> {
          spyOn(GGRC.Utils.CurrentPage, 'getPageType')
            .and.returnValue('Workflow');
        });
        it('when option was false', ()=> {
          vm.attr('expanded', false);

          vm.onClick('element');

          expect(vm.attr('expanded')).toBe(true);
        });

        it('when option was true', ()=> {
          vm.attr('expanded', true);

          vm.onClick('element');

          expect(vm.attr('expanded')).toBe(false);
        });
      });

      it('call select() if page is not Workflow', ()=> {
        spyOn(GGRC.Utils.CurrentPage, 'getPageType')
          .and.returnValue('AnotherType');
        vm.attr('result', true);

        vm.onClick('element');

        expect(vm.select).toHaveBeenCalledWith('element');
      });
    });

    describe('if instance is CycleTaskGroup', ()=> {
      beforeEach(()=> {
        vm.attr('instance', new can.Map({
          type: 'CycleTaskGroup',
        }));
      });

      describe('toggle "expanded" option if page is "Workflow"', ()=> {
        beforeEach(()=> {
          spyOn(GGRC.Utils.CurrentPage, 'getPageType')
            .and.returnValue('Workflow');
        });

        it('when option was false', ()=> {
          vm.attr('expanded', false);

          vm.onClick('element');

          expect(vm.attr('expanded')).toBe(true);
        });

        it('when option was true', ()=> {
          vm.attr('expanded', true);

          vm.onClick('element');

          expect(vm.attr('expanded')).toBe(false);
        });
      });

      it('call select() if page is not Workflow', ()=> {
        spyOn(GGRC.Utils.CurrentPage, 'getPageType')
          .and.returnValue('AnotherType');
        vm.attr('result', true);

        vm.onClick('element');

        expect(vm.select).toHaveBeenCalledWith('element');
      });
    });
  });

  describe('select() method', ()=> {
    let fakeElement;

    beforeEach(()=> {
      fakeElement = {
        closest: jasmine.createSpy().and.returnValue('closest'),
      };
      spyOn(can, 'trigger');
      vm.attr('instance', 'fakeInstance');
      vm.attr('itemSelector', 'fakeSelector');
    });

    it('looks for correct element', ()=> {
      vm.select(fakeElement);

      expect(fakeElement.closest).toHaveBeenCalledWith('fakeSelector');
    });

    it('triggers "selectTreeItem" event', ()=> {
      vm.select(fakeElement);

      expect(can.trigger).toHaveBeenCalledWith(
        'closest',
        'selectTreeItem',
        ['closest', 'fakeInstance']);
    });
  });
});
