from datetime import datetime
from odoo import _, fields, models
from odoo.addons.queue_job.job import DONE, PENDING, STATES, Job


CANCELLED = "cancelled"
STATES = STATES + [(CANCELLED, "Cancelled")]

class QueueJob(models.Model):
  _inherit = 'queue.job'

  state = fields.Selection(STATES, readonly=True, required=True, index=True)
  date_cancelled = fields.Datetime(readonly=True)

  def set_cancelled(self, result=None):
        self.state = CANCELLED
        self.date_cancelled = datetime.now()
        if result is not None:
            self.result = result

  def _change_job_state(self, state, result=None):
    """Change the state of the `Job` object

    Changing the state of the Job will automatically change some fields
    (date, result, ...).
    """
    for record in self:
        job_ = Job.load(record.env, record.uuid)
        if state == DONE:
            job_.set_done(result=result)
            job_.store()
            job_.enqueue_waiting()
        elif state == PENDING:
            job_.set_pending(result=result)
            job_.store()
        elif state == CANCELLED:
            job_.set_cancelled(result=result)
            job_.store()
        else:
            raise ValueError("State not supported: %s" % state)

  def button_cancelled(self):
    result = _("Cancelled by %s") % self.env.user.name
    self._change_job_state(CANCELLED, result=result)
    return True


class SetJobsToCancelled(models.TransientModel):
    _inherit = "queue.requeue.job"
    _name = "queue.jobs.to.cancelled"
    _description = "Cancel all selected jobs"

    def set_cancelled(self):
        jobs = self.job_ids.filtered(
            lambda x: x.state in ("pending", "failed", "enqueued")
        )
        jobs.button_cancelled()
        return {"type": "ir.actions.act_window_close"}