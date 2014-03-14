(function () {
"use strict";

var _jobs = {};
//    _sound = new Audio(__SOUND__);

function sortjob(job){
    var total = 0;
    if (job.time_class == 'past')
        return 'a' + Date.parse(job.due_on);
    else if (job.time_class == 'soon')
        return 'b' + Date.parse(job.due_on);
    else if (job.due_on) 
        return 'c' + Date.parse(job.due_on);
    else
        return 'd';
}



function job_html(job) {
    return ( '<div class="task ' + job.time_class + '" id="' + job.id + '" data-sortpos="'+sortjob(job)+'">' +
                 '<h1>' + __USERS__[job.assignee.id].name.split(' ')[0] + '</h1>' +
                 '<div class="details">' +
                     '<h2>' + job.name + '</h2>' +
                     '<h3>' + job.project.name + '</h3>' +
             '</div></div>' );
}

function get_latest() {
    $.getJSON(__JOBS_API__ + "?" + Date.now() , function(data) {
        try {
            var i, x, current, id,
                remove_index,
                to_remove = Object.keys(_jobs), // to make removing easier...
                projects = $('#projects'),
                to_add = [];

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
                            //_sound.play();
     
                         }

                        _jobs[id].data = current;

                        _jobs[id].el.remove();

                        x = $(job_html(current));
                        _jobs[id].el = x;

                        //projects.isotope('insert', x);
                        projects.append(x);
                        //to_add.push(x);
                    }
                } else {
                    // New item:

                    x = $(job_html(current));
                    _jobs[id] = { data: current, el: x };

                    // projects.isotope('insert', x);
                    projects.append(x);
                }
            }

            // Now remove any items which aren't in the latest list:

            window.j = _jobs;

            for (i=0; i< to_remove.length; i++) {
                //projects.isotope('remove', _jobs[to_remove[i]].el);
                _jobs[to_remove[i]].el.remove();
                delete _jobs[to_remove[i]];

            }

            //projects.isotope('reLayout');
            $('#projects .task').tsort({'order':'asc', attr:'data-sortpos'});

        } catch (e) {
            console.log(e);
        }

        setTimeout(get_latest, 120000);
    }).fail(function() { setTimeout(get_latest, 120000); });;
}

// exports:
window.get_latest = get_latest;
//window.init_isotope = init_isotope;
})();
