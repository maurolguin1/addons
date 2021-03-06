# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 ISA s.r.l. (<http://www.isa.it>).
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
import netsvc
from osv import fields, osv
from tools.translate import _
from openerp import tools
import math
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta


class hr_overtime_type(osv.osv):
	_name = "hr.overtime.type"
	_description = "Overtime Type"
	_columns = {
		'name': fields.char('Description', required=True, size=64),
		'double_validation': fields.boolean('Apply Double Validation', help="If its True then its overtime type have to be validated by second validator"),
		'active': fields.boolean('Active', help="If the active field is set to false, it will allow you to hide the overtime type without removing it."),
	}
hr_overtime_type()

class hr_overtime(osv.osv):
	_name = "hr.overtime"
	_description = "Overtime"
	_order = "date_from asc"

	def create(self, cr, uid, vals, context=None):
		jumlah={}
		#obj = self.browse(cr,uid,ids)[0]
		#jam = float(obj.jam_lembur)
		vals['jam_lembur'] = 0
		jam = float(vals['jam_lembur'])
		#xjamin = int(xjam)
		#xjams = xjam - xjamin
		#con = (xjams*100)/60
		#jam = xjamin + con
		id_over = vals['overtime_type']
		obj=self.pool.get('hr.overtime.jam')
		src=obj.search(cr,uid,[('id','=',id_over)])
		overt = obj.browse(cr,uid,src)[0].jam_ids
		x = 0
		tot = 0
		#import pdb;pdb.set_trace()
		for over in overt  :
			sampai = float(over.sampai)
			dari = float(over.name)
			#import pdb;pdb.set_trace()
			if sampai == 0.0 :
				sampai = float(10000000)
			if dari != 0.0 and jam > 0:
				nx = sampai - dari + 1
				if jam >= nx :
					tot = nx * over.pengali
				elif jam <= nx :
					tot = jam * over.pengali
				jam = jam - nx 
				x = x + tot
		vals['total_jam1'] = x
		tgl = datetime.strptime(vals['date_from'],"%Y-%m-%d %H:%M:%S")
		tanggal = tgl.strftime("%Y-%m-%d")
		#self.write(cr,uid,ids,{'tanggal' : tanggal},context=context)
		vals['tanggal'] = tanggal
		return super(hr_overtime,self).create(cr,uid,vals,context=context)

	def _hitung_lembur(self, cr, uid, ids, arg, vals, context=None):
		jumlah={}
		obj = self.browse(cr,uid,ids)[0]
		jam = float(obj.jam_lembur)
		#xjamin = int(xjam)
		#xjams = xjam - xjamin
		#con = (xjams*100)/60
		#jam = xjamin + con
		overtime_type = obj.overtime_type.jam_ids
		x = 0
		tot = 0
		for over in overtime_type :
			sampai = float(over.sampai)
			dari = float(over.name)
			#import pdb;pdb.set_trace()
			if sampai == 0.0 :
				sampai = float(10000000)
			if dari != 0.0 and jam > 0:
				nx = sampai - dari + 1
				if jam >= nx :
					tot = nx * over.pengali
				elif jam <= nx :
					tot = jam * over.pengali
				jam = jam - nx 
				x = x + tot
		jumlah[obj.id] = x
		self.write(cr,uid,ids,{'total_jam1':x})
		tgl = datetime.strptime(obj.date_to,"%Y-%m-%d %H:%M:%S")
		tanggal = tgl.strftime("%Y-%m-%d")
		self.write(cr,uid,ids,{'tanggal' : tanggal},context=context)
		return jumlah    
	

	def _employee_get(obj, cr, uid, context=None):
		ids = obj.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
		if ids:
			return ids[0]
		return False

	def _compute_number_of_hours(self, cr, uid, ids, name, args, context=None):
		result = {}
		for hol in self.browse(cr, uid, ids, context=context):
			result[hol.id] = hol.number_of_hours_temp         
		return result

	def onchange_dep1(self,cr,uid,ids,employee_id,context=None):
		obj = self.pool.get('hr.employee')
		src = obj.search(cr,uid,[('id','=',employee_id)])
		brw = obj.browse(cr,uid,src)
		dep = False
		for department in brw :
			dep = department.department_id.id
		return {'value': {
			'department_id' : dep,
		}}

	_columns = {
		'name': fields.char('Description', required=True,readonly=True,states={'draft':[('readonly',False)]}, size=64),
		'state': fields.selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('refuse', 'Refused'), 
			('validate1', 'Waiting Second Approval'), ('validate', 'Approved'), ('cancel', 'Cancelled')],
			'State', help='When the overtim request is created the state is \'Draft\'.\n It is confirmed by the user and request is sent to admin, the state is \'Waiting Approval\'.\
			If the admin accepts it, the state is \'Approved\'. If it is refused, the state is \'Refused\'.'),
		'user_id':fields.related('employee_id', 'user_id', type='many2one', relation='res.users', string='User', store=True),
		'users_id':fields.many2one('res.users', 'Creator','Masukan User ID Anda',readonly=True),
		'date_from': fields.datetime('Mulai Lembur dari', readonly=True, states={'draft':[('readonly',False)]}),
		'date_to': fields.datetime('Sampai', readonly=True, states={'draft':[('readonly',False)]}),
		'employee_id': fields.many2one('hr.employee', "Karyawan", select=True, invisible=False, readonly=True, states={'draft':[('readonly',False)]}),
		'manager_id': fields.many2one('hr.employee', 'First Approval', invisible=False, readonly=True),
		'notes': fields.text('Catatan',readonly=True, states={'draft':[('readonly',False)]}),
		'number_of_hours_temp': fields.float('Perkiraan Jam Lembur',readonly=True,states={'draft':[('readonly',False)]}),#states={'draft':[('readonly',False)]}),
		'number_of_hours': fields.function(_compute_number_of_hours, method=True, string='Number of Hours', store=True),
		#'department_id':fields.related('employee_id', 'department_id', string='Department', type='many2one', relation='hr.department', readonly=True),
		'manager_id2': fields.many2one('hr.employee', 'Second Approval', readonly=True, help='This area is automaticly filled by the user who validate the leave with second level (If Leave type need second validation)'),
		'overtime_type_id': fields.many2one("hr.overtime.type", "Type Lembur", required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'department_id' : fields.many2one('hr.department', 'Department',readonly=True,states={'draft':[('readonly',False)]}),
		'overtime_type' : fields.many2one('hr.overtime.jam','Jenis Lembur',required=True,readonly=True, states={'draft':[('readonly',False)]}),
		'total_jam':fields.function(_hitung_lembur,type='float',store=False, readonly=True,string='Total Jam Lembur'),
		'total_jam1':fields.float('jumlah_jam'),
		'jam_lembur':fields.float("Jam Lembur Terealisasi"),
		'lembur_dari':fields.datetime('Perintah Lembur dari Tanggal', readonly=True, states={'draft':[('readonly',False)]}),
		'lembur_sampai':fields.datetime('Sampai', readonly=True, states={'draft':[('readonly',False)]}),
		'tanggal':fields.char('tanggal'),
		'istirahat' : fields.float("istirahat",readonly=True, states={'draft':[('readonly',False)]}),
		'bulan' : fields.char('Bulan'),
		'nominal' : fields.integer("Nominal"),
	}
	_defaults = {
		'employee_id': _employee_get,
		'state': 'draft',
		'users_id': lambda obj, cr, uid, context: uid,
		'bulan' : lambda *a: time.strftime('%Y-%m'),
	}
	_sql_constraints = [
		('date_check', "CHECK ( number_of_hours_temp > 0 )", "The number of hours must be greater than 0 !"),
		('date_check2', "CHECK (date_from < date_to)", "The start date must be before the end date !")
	]

	# TODO: can be improved using resource calendar method
	def _get_number_of_hours(self, date_from, date_to, istirahat):
		"""Returns a float equals to the timedelta between two dates given as string."""
		#import pdb;pdb.set_trace()
		DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
		from_dt = datetime.strptime(date_from, DATETIME_FORMAT)
		to_dt = datetime.strptime(date_to, DATETIME_FORMAT)
		timedelta = to_dt - from_dt
		diff_day1 =float(timedelta.seconds) / 3600
		diff_day2 = int(timedelta.seconds) / 3600
		diff = diff_day1 - diff_day2
		diff1 = (diff*60)/100
		diff_day_awal = diff_day2 + diff1 - istirahat 
		diff_int = int(diff_day_awal)
		pembulatan_dif = diff_day_awal - diff_int
		if pembulatan_dif <= 0.15 :
			diff_day = float(diff_int)
		elif pembulatan_dif >=0.16 and pembulatan_dif <= 0.45 : 
			diff_day = float(diff_int) + 0.30 
		elif pembulatan_dif >= 0.46 :
			diff_day = float(diff_int) + 1 
		return diff_day

	def unlink(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state <>'draft':
				#raise osv.except_osv(_('Warning!'),_('You cannot delete a overtime which is not in draft state !'))
				raise Exception(_('You cannot delete a overtime which is not in draft state !'))
		return super(hr_overtime, self).unlink(cr, uid, ids, context)

	def onchange_date_from1(self, cr, uid, ids, date_to, date_from, istirahat):
		"""
		If there are no date set for date_to, automatically set one 8 hours later than
		the date_from.
		Also update the number_of_days.
		"""
		# date_to has to be greater than date_from
		# if (date_from and date_to) and (date_from > date_to):
		#     raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

		result = {'value': {}}

		# No date_to set so far: automatically compute one 8 hours later
		if date_from and not date_to:
			date_to_with_delta = datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) #+ datetime.timedelta(hours=8)
			result['value']['date_to'] = str(date_to_with_delta)

		# Compute and update the number of days
		if (date_to and date_from) and (date_from <= date_to):
			diff_day = self._get_number_of_hours(date_from, date_to, istirahat)
			result['value']['number_of_hours_temp'] = round(math.floor(diff_day))
		else:
			result['value']['number_of_hours_temp'] = 0

		return result

	def onchange_date_to1(self, cr, uid, ids, date_to, date_from, istirahat):
		"""
		Update the number_of_days.
		"""
		# date_to has to be greater than date_from
		# if (date_from and date_to) and (date_from > date_to):
		#     raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
		obj = self.browse(cr,uid,ids)
		result = {'value': {}}

		# Compute and update the number of days
		if (date_to and date_from) and (date_from <= date_to):
			diff_day = self._get_number_of_hours(date_from, date_to,istirahat)
			result['value']['number_of_hours_temp'] = diff_day #round(math.floor(diff_day))
		else:
			result['value']['number_of_hours_temp'] = 0
		# date_y =  datetime.strptime(date_to,"%Y-%m-%d %H:%M:%S").year
		# date_m =  datetime.strptime(date_to,"%Y-%m-%d %H:%M:%S").month
		# date_d =  datetime.strptime(date_to,"%Y-%m-%d %H:%M:%S").day
		# dates =str(date_y) + "-" + str(date_m) + '-' + str(date_d)
		# result['value']['tanggal'] = dates
		return result

	def set_to_draft(self, cr, uid, ids, *args):
		self.write(cr, uid, ids, {
			'state': 'draft',
			'manager_id': False,
		})
		wf_service = netsvc.LocalService("workflow")
		for id in ids:
			wf_service.trg_create(uid, 'hr.overtime', id, cr)
		return True

	def overtime_validate(self, cr, uid, ids, *args):
		obj_emp = self.pool.get('hr.employee')
		ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
		manager = ids2 and ids2[0] or False
		return self.write(cr, uid, ids, {'state':'validate1', 'manager_id': manager})

	def overtime_validate2(self, cr, uid, ids, *args):
		obj_emp = self.pool.get('hr.employee')
		ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
		manager = ids2 and ids2[0] or False
		self.write(cr, uid, ids, {'state':'validate', 'manager_id2': manager})
		return True

	def overtime_cancel(self, cr, uid, ids, *args):
		for record in self.browse(cr, uid, ids):
			wf_service = netsvc.LocalService("workflow")
			for id in []:
				wf_service.trg_validate(uid, 'hr.overtime', id, 'cancel', cr)

		return True

	def overtime_confirm(self, cr, uid, ids, *args):
		return self.write(cr, uid, ids, {'state':'confirm'})

	def overtime_refuse(self, cr, uid, ids, *args):
		obj_emp = self.pool.get('hr.employee')
		ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
		manager = ids2 and ids2[0] or False
		self.write(cr, uid, ids, {'state': 'refuse', 'manager_id2': manager})
		self.overtime_cancel(cr, uid, ids)
		return True

hr_overtime()

class overtime_jam(osv.osv):
	_name = 'hr.overtime.jam'
	_description = 'pengali jam lembur'

	_columns = {
		'name' : fields.char('Nama Perhitungan Lembur'),
		'jam_ids' : fields.one2many('hr.jam','overtime_jam', 'Perhitungan Jam')  
	}
overtime_jam()

class jam(osv.osv):
	_name = 'hr.jam'

	_columns ={
		'name' :fields.selection([('1','Jam 1'),('2','Jam 2'),('3','Jam 3'),('4','Jam 4'),('5','Jam 5'),('6','Jam 6'),('7','Jam 7'),
			('8','Jam 8'),('9','Jam 9'),('10','Jam 10'),('11','Jam 11'),('12','Jam 12'),('13','Jam 13'),('14','Jam 14'),('15','Jam 15')
			,('16','Jam 16'),('17','Jam 17'),('18','Jam 18'),('19','Jam 19'),('20','Jam 20'),('21','Jam 21'),('22','Jam 22'),('23','Jam 23'),('24','Jam 24')], 'Jam Ke'),
		'sampai' :fields.selection([('1','Jam 1'),('2','Jam 2'),('3','Jam 3'),('4','Jam 4'),('5','Jam 5'),('6','Jam 6'),('7','Jam 7'),
			('8','Jam 8'),('9','Jam 9'),('10','Jam 10'),('11','Jam 11'),('12','Jam 12'),('13','Jam 13'),('14','Jam 14'),('15','Jam 15')
			,('16','Jam 16'),('17','Jam 17'),('18','Jam 18'),('19','Jam 19'),('20','Jam 20'),('21','Jam 21'),('22','Jam 22'),('23','Jam 23'),('24','Jam 24')], 'Sampai Jam Ke'),
		'pengali' :fields.float('Pengali'),
		'overtime_jam' :fields.many2one('hr.overtime.jam'),
	}
jam()

class hr_attendance(osv.osv):
	'''
	PPI Absensi
	'''
	_name = "hr.attendance"
	_inherit = "hr.attendance"
	_description = "Attendance for PPI" 

	def _fill_attendance(self, cr, uid, vals, context=None):
		em = self.pool.get('hr.employee')
		ff = em.search(cr, uid, [('fingerprint_code','=',int(vals['fingerprint_code'])),('no_mesin','=',int(vals['no_mesin'])),('work_location2','=',vals['lokasi_kerja'])], context=context)
		if ff == []:
			raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s tidak ada!") % (vals['fingerprint_code']) ))
		vals['employee_id']=ff[0]
		#import pdb;pdb.set_trace()
		#f= datetime.strptime(vals["name"],'%Y-%m-%d %H:%M:%S')+timedelta(hours=7)
		vals['name_date']=vals['name'][:10]
		if vals['binary_action'] == '1':
			vals['action']='sign_in'
		elif vals['binary_action'] == '0':
			vals['action']='sign_out'
		# elif vals['binary_action'] == 'action':
		#   vals['action']='action'
		#import pdb;pdb.set_trace()
		#vals['name']= str(datetime.strptime(vals["name"],'%Y-%m-%d %H:%M:%S')-timedelta(hours=7))
		return vals

	def _date(self, cr, uid, vals, context=None):
		vals['name'] = str(datetime.strptime(vals["name"],'%Y-%m-%d %H:%M:%S')+timedelta(hours=7))
		return vals

	def isoweekday(self, cr, uid, vals, context=None):
		datas = datetime.strptime(vals["name"],'%Y-%m-%d %H:%M:%S')
		weekday = date.isoweekday(datas)
		return weekday
    #
	# def create(self, cr, uid, vals, context=None):
	# 	# menghitung keterlambatan
	# 	#if vals['binary_action'] == False :
	# 	create_kurang = self.pool.get('hr.tampung.error')
	# 	###########################################################################################
	# 				##import tanpa ada tindakan login atau logout##
	# 	fing_id = vals['fingerprint_code']
	# 	no_mesin = int(vals['no_mesin'])
	# 	#import pdb;pdb.set_trace()
	# 	pal = vals['name']
	# 	vals = self._date(cr, uid, vals, context=None)
	# 	search_emps = self.pool.get('hr.employee').search(cr,uid,[('fingerprint_code','=',fing_id),('no_mesin','=',no_mesin),('work_location2','=',vals['lokasi_kerja'])])
	# 	if search_emps:
	# 		search_emps = self.pool.get('hr.employee').search(cr,uid,[('fingerprint_code','=',fing_id),('no_mesin','=',no_mesin),('work_location2','=',vals['lokasi_kerja'])])[0]
	# 	else :
	# 		return create_kurang.create(cr,uid,{'name':vals['fingerprint_code']})
	# 		#raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s ada yang salah!") % (vals['fingerprint_code']) ))
	# 	search_binary = self.pool.get('hr.contract').search(cr,uid,[('employee_id','=',search_emps)])
	# 	if self.pool.get('hr.contract').browse(cr,uid,search_binary) == [] :
	# 		return create_kurang.create(cr,uid,{'name':vals['fingerprint_code']})
	# 		#raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s ada yang salah!") % (vals['fingerprint_code']) ))
	# 	for emps in self.pool.get('hr.contract').browse(cr,uid,search_binary):
	# 		if emps.date_end == False or emps.date_end >= vals['name'][:10]:
	# 			kon_id = emps.id
	# 		else :
	# 			return create_kurang.create(cr,uid,{'no_mesin':vals['no_mesin'],'lokasi':vals['lokasi_kerja'],'department_id':emps.department_id.id,'date':vals['name'],'name':vals['fingerprint_code'],'employee_id':emps.employee_id.id})
	# 			#raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s ada yang salah!") % (vals['fingerprint_code']) ))
	# 	shift_binary = 1
	# 	if emps.shift_true == True :
	# 		shift_binary = self.pool.get('hr.shift_karyawan').search(cr,uid,[('contract_id','=',kon_id),('date_from','<=',vals['name'][:10]),('date_to','>=',vals['name'][:10])])
	# 	# ########################### koding untuk cek karyawan yg tidak punya shift##########
	# 	if shift_binary == [] :
	# 		x = 1
	# 		values = {
	# 			'employee_id':emps.employee_id.id,
	# 			'date':vals['name']
	# 			}
	#
	# 		emp_id = self.pool.get('tes.attendance').create(cr,uid,values)
	# 		#else :
	# 		return create_kurang.create(cr,uid,{'no_mesin':vals['no_mesin'],'lokasi':vals['lokasi_kerja'],'department_id':emps.department_id.id,'date':vals['name'],'name':vals['fingerprint_code'],'employee_id':emps.employee_id.id})
	# 		#raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s ada yang salah!") % (vals['fingerprint_code']) ))
	# 	else :
	# 	# ###############################################################################
	# 		if emps.shift_true == True :
	# 			for shf in self.pool.get('hr.shift_karyawan').browse(cr,uid,shift_binary):
	# 				schedules = shf.schedule_id.id
	# 		else :
	# 			schedules = emps.working_hours.id
	# 		if schedules == False :
	# 			return create_kurang.create(cr,uid,{'no_mesin':vals['no_mesin'],'lokasi':vals['lokasi_kerja'],'department_id':emps.department_id.id,'date':vals['name'],'name':vals['fingerprint_code'],'employee_id':emps.employee_id.id})
	# 			#raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s ada yang salah!") % (vals['fingerprint_code']) ))
	# 		src_cal = self.pool.get('resource.calendar.attendance').search(cr,uid,[('calendar_id','=',schedules)])
	# 		day = self.isoweekday(cr, uid, vals, context=None)
	# 		x = 1
	# 		daysto2 = 0
	# 		daysto = 0
	# 		hour_from = 1
	# 		c = 0
	# 		for shfatt in self.pool.get('resource.calendar.attendance').browse(cr,uid,src_cal) :
	# 			if int(shfatt.dayofweek)+1 == day :
	# 				daysto1 = shfatt
	# 				if x == 1 :
	# 					daysto = shfatt
	# 				elif x == 2 :
	# 					if emps.shift_true == True :
	# 						if shf.schedule_id.shift_gt_hr == False :
	# 							daysto2 = shfatt
	# 				x = x+1
	# 				c = 1
	# 		cek = 0
	# 		if c == 0 :
	# 			######### cek lembur, jika dia absen di luar shift tapi ternyata dia lembur ########
	# 			obj_ovr = self.pool.get('hr.overtime')
	# 			src_ovr = obj_ovr.search(cr,uid,[('employee_id','=',emps.employee_id.id),('tanggal','=',vals['name'][:10])])
	# 			if src_ovr == [] :
	# 				return create_kurang.create(cr,uid,{'no_mesin':vals['no_mesin'],'lokasi':vals['lokasi_kerja'],'department_id':emps.department_id.id,'date':vals['name'],'name':vals['fingerprint_code'],'employee_id':emps.employee_id.id})
	# 				#raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s ada yang salah!") % (vals['fingerprint_code']) ))
	# 			else :
	# 				for ovr in obj_ovr.browse(cr,uid,src_ovr):
	# 					hr_from = ovr.date_from
	# 					hr_to = ovr.date_to
	# 					ovrs = self._date1(cr, uid, hr_from, hr_to, context=None)
	# 					hour_from = int(ovrs[0][:2])
	# 					hour_to = int(ovrs[1][:2])
	# 					cek = 1
	# 		ddd = float(vals['name'][11]+vals['name'][12])
	# 		if cek != 1	:
	# 			if emps.shift_true == True :
	# 				if shf.schedule_id.shift_gt_hr == True :
	# 					hour_from = daysto1.hour_from
	# 				else :
	# 					hour_from = daysto.hour_from
	# 			else :
	# 				hour_from = daysto.hour_from
	# 			if daysto2 == 0 :
	# 				hour_to = daysto.hour_to
	# 			else :
	# 				hour_to = daysto2.hour_to
	#
	# 			if hour_from-4 <= ddd and  hour_from+2 >= ddd :
	# 				vals['binary_action'] = '1'
	# 			elif hour_to-1  <= ddd :
	# 				vals['binary_action'] = '0'
	# 			else :
	# 				return create_kurang.create(cr,uid,{'no_mesin':vals['no_mesin'],'lokasi':vals['lokasi_kerja'],'department_id':emps.department_id.id,'date':vals['name'],'name':vals['fingerprint_code'],'employee_id':emps.employee_id.id})
	# 				#raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s ada yang salah!") % (vals['fingerprint_code']) ))
	# 		else :
	# 			if hour_from-4 <= ddd and  hour_from+1 > ddd :
	# 				vals['binary_action'] = '1'
	# 			elif hour_from+0.1 <= ddd :
	# 				vals['binary_action'] = '0'
	# 			else :
	# 				return create_kurang.create(cr,uid,{'no_mesin':vals['no_mesin'],'lokasi':vals['lokasi_kerja'],'department_id':emps.department_id.id,'date':vals['name'],'name':vals['fingerprint_code'],'employee_id':emps.employee_id.id})
	# 				#raise osv.except_osv(_('Fingerprint Error!'), _(("Fingerprint ID : %s ada yang salah!") % (vals['fingerprint_code']) ))
	# 		############################################################################################
	# 		vals = self._fill_attendance(cr, uid, vals, context=None)
	# 		# cari login lebih awal dan logout lebih akhir
	# 		newestID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '>=',vals['name']), ('action', '=', 'sign_in')], limit=1, order='name ASC')
	# 			# menghindari dobel login karena old name < inputed name
	# 		newerID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '<',vals['name']), ('action', '=', 'sign_in')], limit=1, order='name ASC')
	# 		#newID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '=',vals['name']), ('action', '=', 'sign_in')], limit=1, order='name ASC')
	# 		latestID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '<=',vals['name']), ('action', '=', 'sign_out')], limit=1, order='name DESC')
	# 			# menghindari dobel logout karena old name > inputed name
	# 		laterID = self.search(cr, uid, [('employee_id', '=', vals['employee_id']), ('name_date', '=',vals['name_date']), ('name', '>',vals['name']), ('action', '=', 'sign_out')], limit=1, order='name DESC')
	# 		# delete login awal and logout akhir
	# 		if newerID and (vals['action'] =='sign_in'):
	# 			vals ['name'] = self.browse(cr, uid, newerID, context=None)[0].name
	# 			# self.unlink(cr, uid, newerID, context=None)
	# 			cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(newerID),))
	# 		if newestID and (vals['action'] =='sign_in'):
	# 			# self.unlink(cr, uid, newestID, context=None)
	# 			cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(newestID),))
	# 		if laterID and (vals['action'] =='sign_out'):
	# 			vals ['name']= self.browse(cr, uid, laterID, context=None)[0].name
	# 			# self.unlink(cr, uid, laterID, context=None)
	# 			cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(laterID),))
	# 		if latestID and (vals['action'] =='sign_out'):
	# 			#execute to overtime disini
	# 			# self.unlink(cr, uid, latestID, context=None)
	# 			cr.execute('DELETE FROM hr_attendance WHERE id IN %s ',(tuple(latestID),))
	# 		# execute to overtime
	# 		if (vals['action'] == 'sign_out') and laterID == [] :
	# 			dates = vals['name']
	# 			ye = datetime.strptime(dates,"%Y-%m-%d %H:%M:%S")
	# 			date_now = ye.strftime("%Y-%m-%d")
	# 			obj_over = self.pool.get('hr.overtime')
	# 			obj_src = obj_over.search(cr,uid, [('employee_id','=',vals['employee_id']),('tanggal','=',date_now),('state','=','validate')])
	# 			for overtime in obj_over.browse(cr,uid,obj_src) :
	# 				dates_to = datetime.strptime(overtime.date_to,"%Y-%m-%d %H:%M:%S")
	# 				dates_from = datetime.strptime(overtime.date_from,"%Y-%m-%d %H:%M:%S")
	# 				if ye >= dates_to :
	# 					obj_over.write(cr, uid, [overtime.id], {'jam_lembur': overtime.number_of_hours_temp})
	# 				else :
	# 					timedelta = ye - dates_from
	# 					diff_day1 =float(timedelta.seconds) / 3600
	# 					diff_day2 = int(timedelta.seconds) / 3600
	# 					diff = diff_day1 - diff_day2
	# 					diff1 = (diff*60)/100
	# 					diff_day = diff_day2 + diff1
	# 					obj_over.write(cr, uid, [overtime.id], {'jam_lembur': diff_day})
	# 		# jika diimport / no mesin exist
	# 		emp 	= vals['employee_id']
	# 		date 	= vals['name']
	# 		action	= vals['binary_action']
	# 		if action == '1' :
	# 			contract_obj	= self.pool.get('hr.contract')
	# 			contract_src	=contract_obj.search(cr, uid, [('employee_id','=', emp),('status','=',True)])
	# 			keterlambatan1 = 100
	# 			for contract in contract_obj.browse(cr,uid,contract_src) :
	# 				if contract.shift_true == True :
	# 					contract_id = contract.id
	# 					shift_obj	= self.pool.get('hr.shift_karyawan')
	# 					shift_src	= shift_obj.search(cr,uid, [('contract_id','=',contract.id),('date_from','<=',date),('date_to','>=',date)])
	# 					for shift in shift_obj.browse(cr,uid,shift_src) :
	# 						for schedule in shift.schedule_id.attendance_ids :
	# 							if keterlambatan1 <= 100 :
	# 								keterlambatan1 = 1+100
	# 								hour 					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').hour
	# 								minute					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').minute
	# 								jum_date 				= hour + float('0.'+str(minute))
	# 								keterlambatan			= jum_date - schedule.hour_from
	# 								vals['keterlambatan']	= keterlambatan
	# 								#schedule.hour_from -
	# 				else:
	# 					working = contract.working_hours.attendance_ids[0]
	# 					#for schedule in working :
	# 					hour 					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').hour
	# 					minute					= datetime.strptime(date,'%Y-%m-%d %H:%M:%S').minute
	# 					jum_date 				= hour + float('0.'+str(minute))
	# 					keterlambatan			= jum_date - working.hour_from
	# 					vals['keterlambatan']	= keterlambatan
	#
	# 		vals['name'] = pal
	# 		if any('no_mesin' in att for att in vals) and vals['no_mesin'] <> '0':
	# 			new_id = super(hr_attendance,self).create(cr,uid,vals,context=context)
	# 			return new_id
	# 		else :
	# 			return super(hr_attendance,self).create(cr,uid,vals,context=context)
hr_attendance()
