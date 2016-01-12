startTime = ""
endTime = ""

times = []
for(var i = 0; i < 24; ++i) {
    for(var j = 0; j < 60; j += 15) {
        times.push(zeroPad(i, 2) + ":" + zeroPad(j, 2));
    }
}

function zeroPad(num, places) {
  var zero = places - num.toString().length + 1;
  return Array(+(zero > 0 && zero)).join("0") + num;
}

        function joinRide(id) {
            $.ajax({
                url: "/api/v1/create/passenger",
                type: "POST",
                data: { carId: id},
                error: function(msg) {
                    console.log(msg);
                },
                success: function(msg) {
                    console.log(msg);
                    location.reload()
                }
            });
        }
        function leaveRide(id) {
            $.ajax({
                url: "/api/v1/remove/passenger",
                type: "POST",
                data: { id: id },
                error: function(msg) {
                    console.log(msg);
                },
                success: function(msg) {
                    console.log(msg);
                    location.reload()
                }
            });
        }
        function deleteRide(id, eventId) {
            $.ajax({
                url: "/api/v1/remove/ride",
                type: "POST",
                data: { id: id },
                error: function(msg) {
                    console.log(msg);
                },
                success: function(msg) {
                    console.log(msg);
                     location = "/view/event/" + eventId;
                }
            });
        }
        function removeEvent(id) {
            $.ajax({
                url: "/api/v1/remove/event",
                type: "POST",
                data: { eventId: id },
                error: function(msg) {
                    console.log(msg);
                },
                success: function(msg) {
                    console.log(msg);
                     location = "/list/event";
                }
            });
        }
    function submit_createRide(id) {
        startTime_d = zeroPad(startTime.getFullYear(), 4) + "-" + zeroPad(startTime.getMonth() + 1, 2)
        + "-" + zeroPad(startTime.getDate(), 2) + " " + zeroPad(startTime.getHours(), 2) + ":"
        + zeroPad(startTime.getMinutes(), 2);

        endTime_d = zeroPad(endTime.getFullYear(), 4) + "-" + zeroPad(endTime.getMonth() + 1, 2)
        + "-" + zeroPad(endTime.getDate(), 2) + " " + zeroPad(endTime.getHours(), 2) + ":"
        + zeroPad(endTime.getMinutes(), 2);

            $.ajax({
                url: "/api/v1/create/ride",
                type: "POST",
                data: {
                    eventId: id,
                    comments: $('#comments').val(),
                    capacity: $('#capacity').val(),
                    departureTime: startTime_d,
                    returnTime: endTime_d
                },
                error: function(msg) {
                    console.log(msg);
                },
                success: function(msg) {
                    console.log(msg);
                     location = "/view/event/" + id;
                }
            });
        }
function submit_createEvent() {
    startTime_d = zeroPad(startTime.getFullYear(), 4) + "-" + zeroPad(startTime.getMonth() + 1, 2)
    + "-" + zeroPad(startTime.getDate(), 2) + " " + zeroPad(startTime.getHours(), 2) + ":"
    + zeroPad(startTime.getMinutes(), 2);

    endTime_d = zeroPad(endTime.getFullYear(), 4) + "-" + zeroPad(endTime.getMonth() + 1, 2)
    + "-" + zeroPad(endTime.getDate(), 2) + " " + zeroPad(endTime.getHours(), 2) + ":"
    + zeroPad(endTime.getMinutes(), 2);

console.log(startTime_d + " " + endTime_d);
    $.ajax({
        url: "/api/v1/create/event",
        type: 'POST',
        data: {
            startTime: startTime_d,
            endTime: endTime_d,
            name: $('#name').val(),
            description: $('#description').val(),
        },
        error: function(msg) {
            console.log(msg);
        },
        success: function(msg) {
            console.log(msg);
            location = "/view/event/" + msg.id
        }
    });
}
function submit_editEvent(event_id) {
    startTime_d = zeroPad(startTime.getFullYear(), 4) + "-" + zeroPad(startTime.getMonth() + 1, 2)
    + "-" + zeroPad(startTime.getDate(), 2) + " " + zeroPad(startTime.getHours(), 2) + ":"
    + zeroPad(startTime.getMinutes(), 2);

    endTime_d = zeroPad(endTime.getFullYear(), 4) + "-" + zeroPad(endTime.getMonth() + 1, 2)
    + "-" + zeroPad(endTime.getDate(), 2) + " " + zeroPad(endTime.getHours(), 2) + ":"
    + zeroPad(endTime.getMinutes(), 2);

console.log(startTime_d + " " + endTime_d);
    $.ajax({
        url: "/api/v1/edit/event",
        type: 'POST',
        data: {
            startTime: startTime_d,
            endTime: endTime_d,
            name: $('#name').val(),
            description: $('#description').val(),
            event: event_id
        },
        error: function(msg) {
            console.log(msg);
        },
        success: function(msg) {
            console.log(msg);
            location = "/view/event/" + event_id
        }
    });
}
