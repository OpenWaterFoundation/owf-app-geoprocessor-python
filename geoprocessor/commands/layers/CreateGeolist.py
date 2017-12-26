import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand

class CreateGeolist(AbstractCommand.AbstractCommand):

    def __init__(self):
        """Initialize the command"""

        # TODO smalers 2017-12-23 Not sure about this syntax...
        #AbstractCommand.AbstractCommand.__init__(self)
        super(CreateGeolist, self).__init__()
        self.command_name = "CreateGeolist"
        self.parameter_list = ["geo_ids", "geolist_id"]


    def run_command(self):

        # notify that this command is running
        print "Running {}".format(self.command_name)

        # get parameter values
        geo_ids = self.return_parameter_value_required("geo_ids")
        geolist_id = self.return_parameter_value_required("geolist_id")

        list_of_geolayers_to_include_in_geolist = []
        error_occurred = False


        # iterate through the user-defined geo_ids (can be geolayer or geolist id)
        for geo_id in geo_ids:

            # if the id is a geolayer id
            if self.is_geolayer_id(geo_id):

                list_of_geolayers_to_include_in_geolist.append(geo_id)

            # if the id is a geolist id
            elif self.is_geolist_id(geo_id):

                geolayer_ids = self.return_geolayer_ids_from_geolist_id(geo_id)
                list_of_geolayers_to_include_in_geolist.extend(geolayer_ids)

            # the id is not a registered geolayer id or a registered geolist id
            else:

                print "ID ({}) is not a valid geolayer id or valid geolist id.".format(geo_id)
                error_occurred = True

        # if there was no error and there is at least one geolayer id to include in the new geolist, append the geolist
        # to the geoprocessor geolist dictionary
        if not error_occurred and list_of_geolayers_to_include_in_geolist:
            self.command_processor.geolists[geolist_id] = list_of_geolayers_to_include_in_geolist

        else:
            print "Error Occurred in CreateGeolist command."
