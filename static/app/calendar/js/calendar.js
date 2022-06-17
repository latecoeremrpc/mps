
   let calendar = null;

    function editEvent(event) {
        $('#event-modal input[name="event-index"]').val(event ? event.id : '');
        $('#event-modal input[name="event-name"]').val(event ? event.name : '');
        $('#event-modal input[name="event-start-date"]').datepicker('update', event ? event.startDate : '');
        $('#event-modal input[name="event-end-date"]').datepicker('update', event ? event.endDate : '');
        $('#event-modal').modal();
    }
    
    function deleteEvent(event) {

        $('#delete-modal input[name="date_id"]').val(event ? event.id : '');


        $('#delete-modal').modal();
    }
    
    function saveEvent() {
        var event = {
            id: $('#event-modal input[name="event-index"]').val(),
            name: $('#event-modal input[name="event-name"]').val(),
            startDate: $('#event-modal input[name="event-start-date"]').datepicker('getDate'),
            endDate: $('#event-modal input[name="event-end-date"]').datepicker('getDate')
        }
        
        var dataSource = calendar.getDataSource();
    
        if (event.id) {
            for (var i in dataSource) {
                if (dataSource[i].id == event.id) {
                    dataSource[i].name = event.name;
                    dataSource[i].startDate = event.startDate;
                    dataSource[i].endDate = event.endDate;
                }
            }
        }
        else
        {
            var newId = 0;
            for(var i in dataSource) {
                if(dataSource[i].id > newId) {
                    newId = dataSource[i].id;
                }
            }
            
            newId++;
            event.id = newId;
        
            dataSource.push(event);
        }
        
        calendar.setDataSource(dataSource);
        $('#event-modal').modal('hide');
    }
    
    $(function() {
        var currentYear = new Date().getFullYear();
    
        calendar = new Calendar('.calendar', { 
            enableContextMenu: true,
            displayWeekNumber:true,
            enableRangeSelection: true,
            contextMenuItems:[
                {
                    text: 'Update',
                    click: editEvent
                },
                {
                    text: 'Delete',
                    click: deleteEvent
                }
            ],
            selectRange: function(e) {
                editEvent({ startDate: e.startDate, endDate: e.endDate });
            },
            mouseOnDay: function(e) {
                if(e.events.length > 0) {
                    var content = '';
                    
                    for(var i in e.events) {
                        content += '<div class="event-tooltip-content">'
                                        + '<div class="event-name" style="color:' + e.events[i].color + '">' + e.events[i].name + '</div>'
                                         + '</div>'
                                    + '</div>';
                    }
                
                    $(e.element).popover({ 
                        trigger: 'manual',
                        container: 'body',
                        html:true,
                        content: content
                    });
                    
                    $(e.element).popover('show');
                }
            },
            mouseOutDay: function(e) {
                if(e.events.length > 0) {
                    $(e.element).popover('hide');
                }
            },
            dayContextMenu: function(e) {
                $(e.element).popover('hide');
            },

            
            dataSource: [
                {%for day in holidays%}
                {
                    id: {{day.id}} ,
                    name: "Day Off: {{day.name}}",
                    startDate: new Date('{{day.holidaysDate|date:'F d,Y'}}'),
                    endDate: new Date('{{day.holidaysDate|date:'F d,Y'}}'),
                    color:'red' 
                    
                },
                {%endfor%}

                {%for day in work %}
                {
                    id: {{day.id}} ,
                    name: "Work Day",
                    startDate: new Date('{{day.date|date:'F d,Y'}}'),
                    endDate: new Date('{{day.date|date:'F d,Y'}}'),
                    color:'blue',
                      
                },
                {%endfor%}
                
            ]
        });
        
        $('#save-event').click(function() {
            saveEvent();
        });
    });
    
