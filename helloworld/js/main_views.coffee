class ErrorMessageView extends Backbone.View
	initialize: =>
		@template = $('#error_msg_tmpl').template()
		@render()
		return @

	render: =>
		tmpl_dict =
			heading : @options.heading
			message : @options.message
		$(@el).html $.tmpl(@template, tmpl_dict)

class LinkSuccessView extends Backbone.View
	initialize: =>
		@template = $('#link_success_tmpl').template()
		@render()
		return @

	render: =>
		tmpl_dict =
			short_url : @options.short_url
		$(@el).html $.tmpl(@template, tmpl_dict)

class MainBitlyView extends Backbone.View
	initialize: =>
		@template = $('#main_bitly_tmpl').template()
		@render()
		return @

	render: =>
		$(@el).html $.tmpl(@template)
	
	events: =>
		'click #submit_btn' : 'get_short_url'
	
	get_short_url: =>
		$('#messages').html ''
		$('#submit_btn').button 'loading'
		if $.trim($('#main_link').val()).length == 0
			$('#submit_btn').button 'reset'
			show_error_msg 'URL Missing', 'You have not entered a URL to shorten. Please enter a URL'
		else
			$.ajax
				url : '/get_short_url'
				data :
					url : $.trim($('#main_link').val())
				type: 'POST'
				dataType : 'json'
				success : (response) ->
					$('#submit_btn').button 'reset'
					if response.success
						view_dict =
							short_url : response.data.short_url
						view = new LinkSuccessView view_dict
						$(view.el).appendTo '#messages'
					else
						show_error_msg 'Error', response.reason
				error: (obj, txt) ->
					$('#submit_btn').button 'reset'
					show_error_msg 'Error', txt

show_error_msg = (heading, message) ->
	view_dict =
		heading : heading
		message : message
	$('#messages').html ''
	view = new ErrorMessageView view_dict
	$(view.el).appendTo '#messages'

# Expose
window.MainBitlyView = MainBitlyView
