import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from bokeh.io import output_file
from bokeh.models import ColumnDataSource, NumeralTickFormatter, Div
from bokeh.models import HoverTool, RadioButtonGroup, CheckboxGroup, CDSView, GroupFilter

from bokeh.io import curdoc

from bokeh.layouts import row, column
from bokeh.models import CustomJS, ColumnDataSource, TapTool,BoxZoomTool, Column
# from bokeh.plotting import figure, output_file, show
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, Select

output_file("dark_minimal.html")
curdoc().theme = 'dark_minimal'

header = Div(text="<link rel=\"stylesheet\" href=\"styles.css\">")
layout = column(header)
curdoc().add_root(layout)

#Data to be displayed
df_final = pd.read_csv('TescoProductData.csv')

columns = list(df_final.columns)
numerical_columns = list(df_final.select_dtypes(include=[np.float]).columns)
categories = list(df_final.Category.unique())
nutrient_list_columns = ['Energy (kJ)', 'Energy (kcal)', 'Fat (g)', 'Saturates (g)', 'Carbohydrates (g)',
						 'Sugars (g)', 'Fibre (g)', 'Protein (g)', 'Salt (g)']

df_final['x'] = df_final['Protein (g)']
df_final['y'] = df_final['Regular_Price']

active_x = 'Protein (g)'
active_y = 'Regular_Price'

active_axes = dict(x=['Protein (g)'],y=['Regular Price'])

# Store the data in a ColumnDataSource
data_source_total = ColumnDataSource(df_final)
data_source = ColumnDataSource(df_final)
axes_source = ColumnDataSource(active_axes)

# We use ints to make it easy to work with in js
filters = {'dry':[1 if x else 0 for x in list(df_final['Category'] == 'dry')],
		   'fresh':[1 if x else 0 for x in list(df_final['Category'] == 'fresh')],
		   'frozen':[1 if x else 0 for x in list(df_final['Category'] == 'frozen')],
		   'bakery':[1 if x else 0 for x in list(df_final['Category'] == 'bakery')]}

view1 = CDSView(source=data_source)

plot_size_and_tools = {'plot_height': 300, 'plot_width': 300,
						'tools':['box_select', 'reset', 'help']}

# Specify the selection tools to be made available
select_tools = ['box_select', 'lasso_select', 'poly_select', 'tap', 'reset']

# Create the figure
fig = figure(plot_height=600,
			 plot_width=900,
			 x_axis_label='Protein Per 100g',
			 y_axis_label='Regular Price',
			 title='{} vs {} For 100g'.format(active_y,active_x),
			 toolbar_location='below',
			 tools=select_tools)

# Format the tooltip
tooltips = [
			('Product','@Product'),
			('Regular Price','\u00a3@{Regular Price}{0.00}'),
			('Fat (g/100g)','@{Fat (g)}{0.00}'),
			('Carbohydrates (g/100g)','@{Carbohydrates (g)}{0.00}'),
			('Protein (g/100g)','@{Protein (g)}{0.00}'),
		   ]

# Add the HoverTool to the figure
fig.add_tools(HoverTool(tooltips=tooltips))

# Add square representing each product
fig.square(x='x',
		   y='y',
		   source=data_source,
		   color='royalblue',
		   selection_color='deepskyblue',
		   nonselection_color='lightgray',
		   nonselection_alpha=0.3,
		   view = view1)

data_table_source = ColumnDataSource(data = {k: [] for k in columns})

# columns = ["Product", 'Regular Price','Amount (g)','Energy (kJ)','Energy (kcal)','Fat (g)','Carbohydrates (g)','Protein (g)','Salt (g)']

data_table_columns = [
		TableColumn(field="Product", title="Product"),
		TableColumn(field='Regular Price', title='Regular Price'),
		TableColumn(field='Amount (g)', title='Amount (g)'),
		TableColumn(field='Energy (kJ)', title='Energy (kJ)'),
		TableColumn(field='Energy (kcal)', title='Energy (kcal)'),
		TableColumn(field='Fat (g)', title='Fat (g)'),
		TableColumn(field='Carbohydrates (g)', title='Carbohydrates (g)'),
		TableColumn(field='Protein (g)', title='Protein (g)'),
		TableColumn(field='Salt (g)', title='Salt (g)'),
	]

data_table = DataTable(columns=data_table_columns, source=data_table_source, width=900)

data_source.selected.js_on_change('indices', CustomJS(args=dict(s1=data_source, s2=data_table_source, columns=columns), code="""
	var data = s1.data;
	var f = cb_obj.indices;
	var d2 = s1.data;
	var d3 = s2.data;
	
	for (var i = 0; i < columns.length; i++) {
		if (columns[i]){
			d3[columns[i]] = [];
		}
	}

	for (var j = 0; j < f.length; j++) {
		for (var i = 0; i < columns.length; i++) {
			if (columns[i]){
				d3[columns[i]].push(d2[columns[i]][f[j]])
			}
		}
	}

	// trigger change on datatable
	s2.change.emit()
"""))

checkbox_group = CheckboxGroup(labels=categories, active=[0, 1, 2, 3])
checkbox_group.js_on_change('active', CustomJS(args=dict(data_source_total=data_source_total, filters=filters, data_source=data_source, checkbox_group=checkbox_group, columns=columns, categories=categories, fig=fig), code="""
	var data = data_source_total.data;
	var data_filtered = data_source.data;
	var filt = Array(filters['dry'].length).fill(0);
	
	for (var j = 0; j < columns.length; j++) {
		data_filtered[columns[j]] = []
	}
	
	function addvector(a,b){
		return a.map((e,i) => e + b[i]);
	}

	for (var q = 0; q < checkbox_group.active.length; q++){
		filt = addvector(filt, filters[categories[checkbox_group.active[q]]])
		//filt = filt + filters[categories[checkbox_group.active[q]]]
	}
	console.log(filt)
	
	for (var x = 0; x < filt.length; x++){
		if (filt[x] == 1){
			for (var j = 0; j < columns.length; j++) {
				data_filtered[columns[j]].push(data[columns[j]][x])
			}
		}
	}
	data_source.change.emit()
"""))

button = RadioButtonGroup(labels=["Per 100g", "Total"], active=0)
button.js_on_change('active', CustomJS(args=dict(data_source=data_source, fig=fig, button=button, axis=fig.yaxis[0], axes_source=axes_source, nutrient_list_columns=nutrient_list_columns), code="""
	var nutrients = nutrient_list_columns;

	if (button.active == 1){
		if (nutrients.includes(axes_source.data['x'][0])){
			var ar3 = [];
			for(var i = 0; i <= data_source.data['x'].length; i++){
				var valu = data_source.data['x'][i] * data_source.data['Amount (g)'][i];
				ar3[i] = valu / 100;
			}
			data_source.data['x'] = ar3;
		}
		if (nutrients.includes(axes_source.data['y'][0])){
			var ar3 = [];
			for(var i = 0; i <= data_source.data['y'].length; i++){
				var valu = data_source.data['y'][i] * data_source.data['Amount (g)'][i];
				ar3[i] = valu / 100;
			}
			data_source.data['y'] = ar3;
		}
		//fig.title = axes_source.data['y'][0] + 'vs.' + axes_source.data['y'][0] + 'For Total'
	}
	if (button.active == 0){
		if (nutrients.includes(axes_source.data['x'][0])){
			var ar3 = [];
			for(var i = 0; i <= data_source.data['x'].length; i++){
				var valu = data_source.data['x'][i] / data_source.data['Amount (g)'][i];
				ar3[i] = valu * 100;
			}
			data_source.data['x'] = ar3;
		}
		if (nutrients.includes(axes_source.data['y'][0])){
			var ar3 = [];
			for(var i = 0; i <= data_source.data['y'].length; i++){
				var valu = data_source.data['y'][i] / data_source.data['Amount (g)'][i];
				ar3[i] = valu * 100;
			}
			data_source.data['y'] = ar3;
		}
		//fig.title = axes_source.data['y'][0] + 'vs.' + axes_source.data['y'][0] + 'For 100g'
	}
	fig.change.emit()
	data_source.change.emit()
"""))

# Add both axis, check if they're part of nutrient list, muiltiply/divide by wieght column.
Y_Axesselect = Select(title="Select Y Axis:", value="Regular Price", options=numerical_columns)
Y_Axesselect.js_on_change('value', CustomJS(args=dict(data_source=data_source, title=fig.title, Y_Axesselect=Y_Axesselect, axis=fig.yaxis[0], axes_source=axes_source, button=button, nutrient_list_columns=nutrient_list_columns), code="""
	var nutrients = nutrient_list_columns;
	axis.axis_label = Y_Axesselect.value
	axes_source.data['y'][0] = Y_Axesselect.value
	data_source.data['y'] = data_source.data[Y_Axesselect.value]
	title.text = axes_source.data['y'][0] + ' vs. ' + axes_source.data['x'][0] + ' For 100g'
	if (button.active == 1){
		if (nutrients.includes(axes_source.data['y'][0])){
			var ar3 = [];
			for(var i = 0; i <= data_source.data['y'].length; i++){
				var valu = data_source.data['y'][i] * data_source.data['Amount (g)'][i];
				ar3[i] = valu / 100;
			}
			data_source.data['y'] = ar3;
		}
		title.text = axes_source.data['y'][0] + ' vs. ' + axes_source.data['x'][0] + ' For Total'
	}
	axes_source.change.emit()
	data_source.change.emit()
	"""))

X_Axesselect = Select(title="Select X Axis:", value="Protein (g)", options=numerical_columns)
X_Axesselect.js_on_change('value', CustomJS(args=dict(data_source=data_source, title=fig.title, X_Axesselect=X_Axesselect, axis=fig.xaxis[0], axes_source=axes_source, button=button, nutrient_list_columns=nutrient_list_columns), code="""
	var nutrients = nutrient_list_columns;
	axis.axis_label = X_Axesselect.value
	axes_source.data['x'][0] = X_Axesselect.value
	data_source.data['x'] = data_source.data[X_Axesselect.value]
	title.text = axes_source.data['y'][0] + ' vs. ' + axes_source.data['x'][0] + ' For 100g'
	if (button.active == 1){
		if (nutrients.includes(axes_source.data['x'][0])){
			var ar3 = [];
			for(var i = 0; i <= data_source.data['x'].length; i++){
				var valu = data_source.data['x'][i] * data_source.data['Amount (g)'][i];
				ar3[i] = valu / 100;
			}
			data_source.data['x'] = ar3;
		}
		title.text = axes_source.data['y'][0] + ' vs. ' + axes_source.data['x'][0] + ' For Total'
	}
	axes_source.change.emit()
	data_source.change.emit()
	"""))

controls = [checkbox_group, button]
axes_controls = Column(Y_Axesselect, X_Axesselect, *controls)

level = row([fig, axes_controls])
layout_2 = Column(level, data_table)
output_file("plot.html") #Save html file

# Visualize
show(layout_2)