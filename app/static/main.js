(function () {
"use strict";

var _jobs = {},
    _sound = new Audio(__SOUND__);


function job_html(job) {
    return ( '<div class="task ' + job.time_class + '" id="' + job.id + '">' +
                 '<h1>' + __USERS__[job.assignee.id].name.split(' ')[0] + '</h1>' +
                 '<div class="details">' +
                     '<h2>' + job.name + '</h2>' +
                     '<h3>' + job.project.name + '</h3>' +
             '</div></div>' );
}

function init_isotope() {
    $('#projects').isotope({
        getSortData:{
            class: function(e){
                var fullclass = e.attr('class');
                if (fullclass.contains('past'))
                    return 0;
                else if (fullclass.contains('soon'))
                    return 1;
                else
                    return 2;
                }
            },
        sortBy:'class'});
};

function get_latest() {
    $.get(__JOBS_API__ + "?" + Date.now() , function(data) {
        var i, x, current, id, remove_index,
            to_remove = Object.keys(_jobs); // to make removing easier...

        for(i=0;i<data['tasks'].length;i++) {
            // loop local vars:
            current = data['tasks'][i];
            id = current.id + '_' + current.project.id;
            
            // This item is in the new data, so we don't need to remove it:
            remove_index = to_remove.indexOf(id);
            if (remove_index > -1) {
                to_remove.splice(remove_index, 1);
            }

            // And check for updates to the item:

            if (_jobs.hasOwnProperty(id)) {
                if ( JSON.stringify(current) !== JSON.stringify(_jobs[id].data) ) {
                    // Item still here, but changed!

                    if ((current.time_class == 'past') &&
                        (_jobs[id].data.time_class !== 'past')) {
                        // here's a little sarcasm...
                        _sound.play();
                    }

                    _jobs[id].data = current;

                    $('#projects').isotope('remove', _jobs[id].el);

                    x = $(job_html(current));
                    _jobs[id].el = x;

                    $('#projects').isotope('insert', x);
                }
            } else {
                // New item:

                x = $(job_html(current));
                _jobs[id] = { data: current, el: x };

                //$('#projects').append(x);
                $('#projects').isotope('insert', x);
            }
        }

        // Now remove any items which aren't in the latest list:

        window.j = _jobs;

        for (i=0; i< to_remove.length; i++) {
            $('#projects').isotope('remove', _jobs[to_remove[i]].el);
            delete _jobs[to_remove[i]];

        }

        setTimeout(get_latest, 120000);
    });
}

// exports:
window.get_latest = get_latest;
window.init_isotope = init_isotope;
})();
