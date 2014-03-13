(function () {
"use strict";

var _jobs = {},
    _sound = new Audio(__SOUND__);

function job_html(job) {
    return ( '<div class="task ' + job.time_class + '" id="' + job.id + '">' +
                 '<h2>' + job.name + '</h2>' +
                 '<h3>' + job.project.name + '</h3>' +
             '</div>' );
}


function get_latest() {
    $.get(__JOBS_API__, function(data) {
        var i, x, current, id;
        for(i=0;i<data['tasks'].length;i++) {
            current = data['tasks'][i];
            id = current.id + '_' + current.project.id;
            if (_jobs.hasOwnProperty(id)) {
                if ( JSON.stringify(current) !== JSON.stringify(_jobs[id].data) ) {
                    if ((current.time_class == 'past') &&
                        (_jobs[id].data.time_class !== 'past')) {
                        // here's a little sarcasm...
                        _sound.play();
                        console.log(current.time_class, _jobs[id].data.time_class, current.name);
                    }

                    _jobs[id].data = current;
                    x = $(job_html(current));
                    _jobs[id].el.replaceWith(x);
                    _jobs[id].el = x;
                }
            } else {
                x = $(job_html(current));
                _jobs[id] = { data: current, el: x };

                $('#projects').append(x);
            }
        }
        setTimeout(get_latest, 100000);
    });
}

window.get_latest = get_latest;
})();
