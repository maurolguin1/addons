# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# Generated by the OpenERP plugin for Dia !
from openerp.osv import fields,osv
import time
from datetime import date


class netpro_member(osv.osv):
    _name = 'netpro.member'
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'member_no'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', 
            required=True, select=True, ondelete='cascade'),
        'policy_id': fields.many2one('netpro.policy', 'Policy', required=True, domain='[("state","=","approved"),]'),
        'policy_holder': fields.related('policy_id', 'policy_holder_id', 
            relation='res.partner', type='many2one', store=True, string='Policy Holder'),
        'policy_category': fields.related('policy_id', 'policy_category_id', 
            relation='netpro.policy_category', type='many2one', store=False, string='Policy Category'),
        'insurance_period_start': fields.date('Insurance Period Start', required=True),
        'insurance_period_end': fields.date('Insurance Period End', required=True),
        'member_no': fields.char('Member No.',help="Kosongkan untuk diisi oleh sistem"),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'census_no': fields.selection([('0','0 = Employee'),('1','1 = Spouse'),('2','2 = 1st Child')],'Census No.'),
        'gender_id': fields.many2one('netpro.gender', 'Sex'),
        'marital_status': fields.many2one('netpro.marital_status', 'Marital Status'),
        'mobile_phone': fields.char('Mobile Phone'),
        'date_of_birth': fields.date('DoB'),
        'age': fields.integer('Age'),
        'birth_place': fields.char('Birth Place'),
        'salary': fields.float('Salary'),
        'vip': fields.boolean('VIP'),
        'black_listed': fields.boolean('Black Listed '),
        'hold_car_swipe_claim': fields.boolean('Hold Card Swipe And Claim'),
        'remarks': fields.text('Remarks'),
        'class_id': fields.many2one('netpro.class', 'Class', required=True),
        'membership': fields.many2one('netpro.membership', 'Membership', required=True),
        'card_no': fields.char('Card No'),
        'register_no': fields.char('Register No.'),
        'period_start': fields.date('Period Start'),
        'period_end': fields.date('Period End'),
        'stnc': fields.date('STNC'),
        'group_id': fields.char('Group ID'),
        'payor_id': fields.many2one('res.partner', 'Payor'),
        'premium_type_id': fields.many2one('netpro.premium_type', 'Premium Type'),
        'area_id': fields.many2one('res.country.state', 'Area'),
        'pre_existing_waived': fields.boolean('Pre Existing Waived'),
        'exclude_this_member': fields.boolean('Exclude this Member'),
        'dummy_member': fields.boolean('Dummy Member'),
        'mno': fields.float('MNO', readonly=True),
        'pmno': fields.integer('PMNO', readonly=True),
        'state': fields.selection([('draft','Draft'), ('actived','Actived'), ('nonactive', 'Non Active')],'Policy Status'),
        'status': fields.selection([('draft','Draft'), ('actived','Actived'), ('nonactive', 'Non Active')],'Policy Status'),
        'trans_type': fields.char('Trans. Type', readonly=True),
        'suspend_tpa': fields.boolean('Suspend TPA', readonly=True),
        'account_no': fields.char('Account No'),
        'account_name': fields.char('Account Name'),
        'bank': fields.char('Bank'),
        'bank_name': fields.char('Bank Name'),
        'bank_branch': fields.char('Bank Branch'),
        'company_address': fields.text('Address'),
        'title': fields.char('Title'),
        'division': fields.char('Division'),
        'branch': fields.char('Branch'),
        'occupation': fields.char('Occupation'),
        'id_no': fields.char('ID No'),
        'province': fields.char('Province'),
        'height': fields.integer('Height'),
        'weight': fields.integer('Weight'),
        'member_plan_ids': fields.one2many('netpro.member_plan', 'member_id', 'Plans', ondelete='cascade'),
        'family_ids': fields.one2many('netpro.member', 'parent_id', 'Families', ondelete='cascade'),
        'claim_history_ids': fields.one2many('netpro.member_claim_history', 'member_id', 'Claim Histories', ondelete='cascade'),
        'parent_id': fields.many2one('netpro.member', 'Parent'),
        'created_by_id': fields.many2one('res.users', 'Created By', readonly=True),
        'upd_code' : fields.selection([('d','D'),('n','N'),('r','R'),('l','L'),('u','U')], 'Update Code'),
        'upd_date' : fields.date('Update Date'),
        'masa_tunggu': fields.boolean('Masa Tunggu'),
        'masa_tunggu_value': fields.integer('Lama Masa Tunggu'),
        'grace_period': fields.boolean('Grace Period'),
        'grace_period_value': fields.integer('Grace Period Days'),
        'member_policy_exception_check' : fields.boolean('Policy Exception'),
        'member_policy_exception_ids' : fields.one2many('netpro.member_policy_exception','member_id','Policy Exception', ondelete="cascade"),
    }

    _defaults = {
        'status'                    : 'draft',
        'insurance_period_start'    : lambda *a : time.strftime("%Y-%m-%d"),
        'insurance_period_end'      : lambda *a : time.strftime("%Y-%m-%d"),
        'created_by_id'             : lambda obj, cr, uid, context: uid,
        'upd_date'                  : lambda *a : time.strftime("%Y-%m-%d"),
    }

    _sql_constraints = [
        ('member_no_unique', 'UNIQUE(member_no)', 'Member No. Must be Unique!'),
    ]

    def create(self, cr, uid, vals, context=None):
        if not vals['member_no']:
            vals.update({
                'member_no' : self.pool.get('ir.sequence').get(cr, uid, 'member_seq') or '/',
            })
        return super(netpro_member, self).create(cr, uid, vals, context=context)

    def action_confirm(self,cr,uid,ids,context=None):
        # create schedule plan
        self.create_plan_schedule(cr,uid,ids,context=context)        
        #set to "actived" state
        self.write(cr,uid,ids,{'status':'actived'},context=context)
        return 
    
    def action_cancel(self,cr,uid,ids,context=None):
        #set to "draft" state
        return self.write(cr,uid,ids,{'status':'draft'},context=context)
    
    def action_nonactive(self,cr,uid,ids,context=None):
        #set to "nonactive" state
        return self.write(cr,uid,ids,{'status':'nonactive'},context=context) 

    def create_plan_schedule(self, cr, uid, ids, context=None):
        #import pdb;pdb.set_trace()
        pplan_bnft_obj      = self.pool.get('netpro.product_plan_benefit')
        member_plan_obj     = self.pool.get('netpro.member_plan')
        member_plan_det_obj = self.pool.get('netpro.member_plan_detail')
        self_obj            = self.browse(cr,uid,ids[0],context=context)
        # jika belum ada schedule
        if not self_obj.member_plan_ids:
            if self_obj.policy_id:
                #jika policy ny sdh aproved
                if self_obj.policy_id.state == 'approved':
                    plan_schedule_ids = self_obj.policy_id.plan_schedule_ids
                    if plan_schedule_ids:
                        for schedule in plan_schedule_ids:
                            #jika plan for sama dan classnya sama
                            if schedule.plan_for == self_obj.membership.name and schedule.class_id.id == self_obj.class_id.id :
                                #create schedule
                                plan_schedule_id = member_plan_obj.create(cr,uid,{'member_id': ids[0],
                                                                                'plan_schedule_id': schedule.id,
                                                                                'bamount' : schedule.bamount,
                                                                                'plan_for':self_obj.membership.name})  
                                # jika ada detail benefitnya maka di create juga benefit yang sama
                                if schedule.plan_schedule_detail_benefit_schedule_ids :
                                    for benefit in schedule.plan_schedule_detail_benefit_schedule_ids:
                                        member_plan_det_obj.create(cr,uid,{'member_plan_id':plan_schedule_id,
                                                                            'benefit_id': benefit.benefit_id.id,
                                                                            'bamount':benefit.bamount})                                    

        return  True

    def onchange_class(self, cr, uid, ids, parent_id, context=None):

        results = {}
        if not parent_id:
            return results 
        member_obj = self.pool.get('netpro.member') 
        parent_class = member_obj.browse(cr,uid,parent_id)

        results = {
            'value' : {
                'class_id' : parent_class.class_id.id
            }
        }
        return results

    def onchange_policy_member(self, cr, uid, ids, policy_id, context=None):
        results = {}
        if not policy_id:
            return results

        policy_obj = self.pool.get('netpro.policy')
        policy_data = policy_obj.browse(cr,uid,policy_id)

        results = {
            'value' : {
                'insurance_period_start'    : policy_data.insurance_period_start,
                'insurance_period_end'      : policy_data.insurance_period_end,
                'policy_holder'             : policy_data.policy_holder_id.id,
                'policy_category'           : policy_data.policy_category_id.id,
            }
        }
        return results

    def onchange_DoB(self, cr, uid, ids, date_of_birth):
        result = {}
        if date_of_birth:
            d = time.strptime(date_of_birth,"%Y-%m-%d")
            delta = date.today() - date(d[0], d[1], d[2])
            usia = delta.days / 365.2425
            result = int(usia)
        return {'value':{'age':result}}

    def onchange_family(self, cr, uid, ids, fam_ids, policy_id, context=None):
        
        if policy_id:
            raise osv.except_osv(_('Warning!'),_("Please choose Policy for this member") )

        policy_obj = self.pool.get('netpro.policy').browse(cr, uid, policy_id, context=None)

        if policy_obj.policy_category_id.name == 'Individual':
            if policy_obj.individual_member_limit > 0:
                if len(fam_ids) > policy_obj.individual_member_limit:
                    raise osv.except_osv(_('Error!'),_("Cannot add new member to this policy due to Individual Policy rule(s).") )

        return

netpro_member()

class netpro_member_policy_exception(osv.osv):
    _name = 'netpro.member_policy_exception'
    _columns = {
        'member_id' : fields.many2one('netpro.member', 'Member'),
        'diagnosis_id' : fields.many2one('netpro.diagnosis', 'Diagnosis'),
    }
netpro_member_policy_exception()


class netpro_member_plan(osv.osv):
    _name = 'netpro.member_plan'
    _rec_name = 'product_plan'
    _columns = {
        'member_id': fields.many2one('netpro.member', 'Member'),
        'plan_schedule_id': fields.many2one('netpro.plan_schedule', 'PPlan'),
        'product_plan': fields.related('plan_schedule_id','product_plan_id', 'product_plan_base_id', 
            relation="netpro.product_plan_base",
            type='many2one', string='Product Plan', store=True, readonly=True),

        'bamount': fields.float('BAmount'),
        'plan_limit': fields.float('Plan Limit'),
        'remaining_limit': fields.float('Remaining Limit'),
        'family_limit': fields.float('Family Limit'),
        'family_remaining_limit': fields.float('Family Remaining Limit'),
        'hi_plan': fields.boolean('Hi Plan'),
        'aso': fields.boolean('ASO'),
        'excess': fields.char('Excess'),
        'per_disability': fields.boolean('Per Disability'),
        'member_plan_detail_ids': fields.one2many('netpro.member_plan_detail', 'member_plan_id', 'Member Plan Details', ondelete='cascade'),
        'plan_for': fields.char('Plan For',readonly="True"),
    }
netpro_member_plan()

class netpro_member_plan_detail(osv.osv):
    _name = 'netpro.member_plan_detail'
    _rec_name = 'benefit_id'
    _columns = {
        'member_plan_id': fields.many2one('netpro.member_plan', 'Member Plan'),
        'benefit_id' : fields.many2one('netpro.benefit', 'Benefit'),
        'benefit_code' : fields.related('benefit_id', 'code' , type="char", 
            relation="netpro.benefit", string="Benefit Code", store=True),
        'reim': fields.float('Reim'),
        'provider_limit': fields.float('Provider Limit'),
        'non_provider_limit': fields.float('Non Provider Limit'),
        'unit': fields.char('Unit'),
        'usage': fields.float('Usage'),
        'remaining': fields.float('Remaining'),
    }
netpro_member_plan_detail()

class netpro_member_claim_history(osv.osv):
    _name = 'netpro.member_claim_history'
    _rec_name = 'claim_id'
    _columns = {
        'member_id': fields.many2one('netpro.member', 'Member'),
        'claim_id': fields.many2one('netpro.claim', 'Claim'),
    }
netpro_member_claim_history()

class netpro_policy(osv.osv):
    _name = 'netpro.policy'
    _inherit = 'netpro.policy'
    _columns = {
        'member_ids' : fields.one2many('netpro.member','policy_id','Member', ondelete="cascade")
    }
netpro_policy()

class netpro_area(osv.osv):
    _name = 'netpro.area'
    _columns={
    'name':fields.char("Name"),
    'code':fields.char("Code"),
    }
netpro_area()