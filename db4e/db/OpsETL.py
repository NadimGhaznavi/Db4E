class OpsETL:

    def __init__(self, ops_db: OpsDb):
        self.ops_db = ops_db

    def add_remote_xmrig_deployment(self, xmrig):
        self.ops_db.add_remote_xmrig_deployment(xmrig)

    def get_ops_summary(self):
        now = datetime.now().replace(microsecond=0)
        summary = []
        summary_dict = {}

        # Grab all current uptime docs
        current = self.ops_db.db.find_many(
            self.ops_db.ops_col, {DMongo.DOC_TYPE: DOps.CURRENT_UPTIME}
        )

        # Grab all total uptime docs
        totals = self.ops_db.db.find_many(
            self.ops_db.ops_col, {DMongo.DOC_TYPE: DOps.TOTAL_UPTIME}
        )
        totals_map = {(t[DMongo.ELEMENT_TYPE], t[DMongo.INSTANCE]): t for t in totals}

        for c in current:
            key = (c[DMongo.ELEMENT_TYPE], c[DMongo.INSTANCE])
            total_event = totals_map.get(key)

            # If still running, compute delta from START_TIME to now
            if c[DOps.STOP_TIME] is None:
                cur_uptime = now - c[DOps.START_TIME]
            else:
                cur_uptime = c[DOps.TOTAL_UPTIME]

            total_uptime = total_event[DOps.TOTAL_UPTIME] if total_event else cur_uptime

            # Convert the total_uptime (secs) into a datetime.timedelta object
            if type(total_uptime) == int:
                total_uptime = str(timedelta(seconds=total_uptime))

            if type(cur_uptime) == int:
                cur_uptime = str(timedelta(seconds=cur_uptime))

            summary_dict[c[DMongo.ELEMENT_TYPE] + "-" + c[DMongo.INSTANCE]] = {
                DMongo.ELEMENT_TYPE: c[DMongo.ELEMENT_TYPE],
                DMongo.INSTANCE: c[DMongo.INSTANCE],
                DOps.CURRENT_UPTIME: str(cur_uptime),
                DOps.TOTAL_UPTIME: str(total_uptime),
            }

        for key in summary_dict.keys():
            summary.append(summary_dict[key])

        return sorted(
            summary, key=lambda x: (x[DMongo.ELEMENT_TYPE], x[DMongo.INSTANCE])
        )

    def get_uptime(self, elem_type, instance):
        rec = self.ops_db.get_uptime(elem_type, instance)
        if not rec:
            return 0
        return rec[DOps.TOTAL_UPTIME]
