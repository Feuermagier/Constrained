from IPython import display
import ipywidgets as widgets
from traitlets import Unicode, validate

javascript = '''
require.undef("constrained")

define("constrained", ["@jupyter-widgets/base"], function(widgets) {
    let view = widgets.DOMWidgetView.extend({
        render: function() {
            this.svg_changed();
            this.model.on("change:svg", this.svg_changed, this);
        },

        svg_changed: function() {
            this.el.innerHTML = this.model.get("svg");
        }
    });

    return {
        ConstrainedView : view
    };
});
'''

display.display(display.Javascript(javascript))

class ConstrainedWidget(widgets.DOMWidget):
    _view_name = Unicode("ConstrainedView").tag(sync=True)
    _view_module = Unicode("constrained").tag(sync=True)
    _view_module_version = Unicode('0.1.0').tag(sync=True)
    svg = Unicode("").tag(sync=True)
