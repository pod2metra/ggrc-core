# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

import ggrc.builder
from flask import request, render_template, current_app
from ggrc.rbac import permissions
from ggrc.services.common import \
    ModelView, as_json, inclusion_filter, filter_resource
from ggrc.utils import benchmark
from werkzeug.exceptions import Forbidden


class BaseObjectView(ModelView):
    model_template = '{model_plural}/show.haml'
    base_template = 'base_objects/show.haml'

    def dispatch_request(self, *args, **kwargs):
        method = request.method.lower()

        if method == 'get':
            if self.pk in kwargs and kwargs[self.pk] is not None:
                return self.get(*args, **kwargs)
            else:
                # No `pk` given; fallthrough for now
                pass
        else:
            # Method not supported; fallthrough for now
            pass

        raise NotImplementedError()

    def get_context_for_object(self, obj):
        return {
            'instance': obj,
            'controller': self,
            'instance_json': lambda: self.get_object_json(obj)
        }

    def get_object_json(self, obj):
        """Returns object json"""
        with benchmark("Get object JSON"):
            return as_json({
                self.model._inflector.table_singular:
                filter_resource(
                    ggrc.builder.json.publish_representation(
                        ggrc.builder.json.publish(obj, (), inclusion_filter)))
            })

    def get_model_template_paths_for_object(self, obj):
        # Generate lookup paths for templates based on inheritance
        return [
            self.model_template.format(
                model_plural=model._inflector.table_plural)
            for model in self.model.mro() if hasattr(model, '__table__')
        ]

    def render_template_for_object(self, obj):
        context = self.get_context_for_object(obj)
        template_paths =\
            self.get_model_template_paths_for_object(obj) + [self.base_template]
        return render_template(template_paths, **context)

    def get(self, id):
        with benchmark("Query for object"):
            obj = self.get_object(id)
        if obj is None:
            return self.not_found_response()
        if 'Accept' in self.request.headers and \
           'text/html' not in self.request.headers['Accept']:
            return current_app.make_response(
                ('text/html', 406, [('Content-Type', 'text/plain')]))
        if not permissions.is_allowed_read(self.model.__name__, obj.id,
                                           obj.context_id):
            raise Forbidden()
        if not permissions.is_allowed_view_object_page_for(obj):
            raise Forbidden()

        with benchmark("Render"):
            rendered_template = self.render_template_for_object(obj)

        # FIXME: Etag based on rendered output, or object itself?
        # if 'If-None-Match' in self.request.headers and \
        #    self.request.headers['If-None-Match'] == self.etag(object_for_json):
        #  return current_app.make_response((
        #    '', 304, [('Etag', self.etag(object_for_json))]))

        return rendered_template

    @classmethod
    def add_to(cls, app, url, model_class=None, decorators=()):
        if model_class:
            cls_name = '{0}ObjectView'.format(model_class.__name__)
            view_class = type(
                cls_name, (cls, ), {
                    '_model': model_class,
                    'base_url_for': classmethod(lambda cls: url),
                })
            import ggrc.views
            setattr(ggrc.views, model_class.__name__, view_class)
        else:
            view_class = cls

        view_func = view_class.as_view(view_class.endpoint_name())
        view_func = cls.decorate_view_func(view_func, decorators)
        view_route = '{url}/<{type}:{pk}>'.format(
            url=url, type=cls.pk_type, pk=cls.pk)
        app.add_url_rule(
            view_route,
            view_class.endpoint_name(),
            view_func=view_func,
            methods=['GET'])
