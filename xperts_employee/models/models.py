# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class xperts_offboarding_reason(models.Model):
    _name = 'xperts.offboarding.reasons'
    name = fields.Char()


class partner_project(models.Model):
    _inherit = 'res.partner'

    project = fields.Many2many('xperts.project','partner_project_rel','partner_id','project_id')

class sales_project(models.Model):
    _inherit = 'sale.order'

    project = fields.Many2one('xperts.project')
    batch_lines_by = fields.Selection([('no','Do Not Batch Lines'),('proj','Project'),('emp','Employee')])

    @api.onchange('project')
    def _onchange_project(self):
        if self.project:
            if self.batch_lines_by == 'emp':
                emp_list = self.env['hr.employee'].search([('project','=',self.project.id)])
                sale_order_line_list = []
                for emp in emp_list:
                    sale_order_line_list.append((0,0,{
                    'product_id':emp.service_id.id,
                    'name':emp.service_id.name,
                    'product_uom_qty':1,
                    'price_unit':emp.service_id.list_price,
                    'tax_id':emp.service_id.taxes_id
                    }))
                self.write({'order_line':sale_order_line_list})
            elif self.batch_lines_by == 'proj':
                sale_order_line_list = []
                sale_order_line_list.append((0,0,{
                'product_id':self.project.service_id.id,
                'name':self.project.service_id.name,
                'product_uom_qty':1,
                'price_unit':self.project.service_id.list_price,
                'tax_id':self.project.service_id.taxes_id
                }))
                self.write({'order_line':sale_order_line_list})
            else:
                pass


class invoice_project(models.Model):
    _inherit = 'account.move'

    project = fields.Many2one('xperts.project')
    batch_lines_by = fields.Selection([('no','Do Not Batch Lines'),('proj','Project'),('emp','Employee')])
    project_contract = fields.Many2one('xperts.project.contract')
    @api.onchange('project')
    def _onchange_project(self):
        if self.project:
            self.project_contract = self.project.project_contract.id
            if self.batch_lines_by == 'emp':
                emp_list = self.env['hr.employee'].search([('project','=',self.project.id)])
                invoice_line_ids_list = []
                for emp in emp_list:
                    invoice_line_ids_list.append((0,0,{
                    'product_id':emp.service_id.id,
                    'name':emp.service_id.name,
                    'quantity':1,
                    'price_unit':emp.service_id.list_price,
                    'tax_ids':emp.service_id.taxes_id,
                    'move_id':self.id
                    }))
                self.write({'invoice_line_ids':invoice_line_ids_list})
            elif self.batch_lines_by == 'proj':
                invoice_line_ids_list = []
                invoice_line_ids_list.append((0,0,{
                'product_id':self.project.service_id.id,
                'name':self.project.service_id.name,
                'quantity':1,
                'price_unit':self.project.service_id.list_price,
                'tax_ids':self.project.service_id.taxes_id,
                'move_id':self.id
                }))
                self.write({'invoice_line_ids':invoice_line_ids_list})
            else:
                pass
            # if self.type in ['out_invoice','out_refund']:

class xperts_project_contract(models.Model):
    _name = 'xperts.project.contract'

    name = fields.Char("Contract")


class rep_cert(models.AbstractModel):
    _name = 'report.xperts_employee.paysliprepinher'

    def get_details_by_rule_category(self, payslip_lines):
        PayslipLine = self.env['hr.payslip.line']
        RuleCateg = self.env['hr.salary.rule.category']

        def get_recursive_parent(current_rule_category, rule_categories=None):
            if rule_categories:
                rule_categories = current_rule_category | rule_categories
            else:
                rule_categories = current_rule_category

            if current_rule_category.parent_id:
                return get_recursive_parent(current_rule_category.parent_id, rule_categories)
            else:
                return rule_categories

        res = {}
        result = {}

        if payslip_lines:
            self.env.cr.execute("""
                SELECT pl.id, pl.category_id, pl.slip_id FROM hr_payslip_line as pl
                LEFT JOIN hr_salary_rule_category AS rc on (pl.category_id = rc.id)
                WHERE pl.id in %s
                GROUP BY rc.parent_id, pl.sequence, pl.id, pl.category_id
                ORDER BY pl.sequence, rc.parent_id""",
                (tuple(payslip_lines.ids),))
            for x in self.env.cr.fetchall():
                result.setdefault(x[2], {})
                result[x[2]].setdefault(x[1], [])
                result[x[2]][x[1]].append(x[0])
            for payslip_id, lines_dict in result.items():
                res.setdefault(payslip_id, [])
                for rule_categ_id, line_ids in lines_dict.items():
                    rule_categories = RuleCateg.browse(rule_categ_id)
                    lines = PayslipLine.browse(line_ids)
                    level = 0
                    for parent in get_recursive_parent(rule_categories):
                        res[payslip_id].append({
                            'rule_category': parent.name,
                            'name': parent.name,
                            'code': parent.code,
                            'level': level,
                            'total': sum(lines.mapped('total')),
                        })
                        level += 1
                    for line in lines:
                        res[payslip_id].append({
                            'rule_category': line.name,
                            'name': line.name,
                            'code': line.code,
                            'total': line.total,
                            'level': level
                        })
        return res

    def get_lines_by_contribution_register(self, payslip_lines):
        result = {}
        res = {}
        for line in payslip_lines.filtered('register_id'):
            result.setdefault(line.slip_id.id, {})
            result[line.slip_id.id].setdefault(line.register_id, line)
            result[line.slip_id.id][line.register_id] |= line
        for payslip_id, lines_dict in result.items():
            res.setdefault(payslip_id, [])
            for register, lines in lines_dict.items():
                res[payslip_id].append({
                    'register_name': register.name,
                    'total': sum(lines.mapped('total')),
                })
                for line in lines:
                    res[payslip_id].append({
                        'name': line.name,
                        'code': line.code,
                        'quantity': line.quantity,
                        'amount': line.amount,
                        'total': line.total,
                    })
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        payslips = self.env['hr.payslip'].search([('date_from','>=',docs.date_from),('date_to','<=',docs.date_to),('employee_id','=',self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).id)])
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            # 'time': time,
            'payslip': payslips,
            'get_details_by_rule_category': self.get_details_by_rule_category(payslips.mapped('details_by_salary_rule_category').filtered(lambda r: r.appears_on_payslip)),
            'get_lines_by_contribution_register': self.get_lines_by_contribution_register(payslips.mapped('line_ids').filtered(lambda r: r.appears_on_payslip)),
        }
        print(docargs)
        return docargs

class rep_sal(models.AbstractModel):
    _name = 'report.xperts_employee.salarycertwiz'

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            # 'time': time,
            'payslip': self.env['hr.payslip'].search([('employee_id','=',self.env['hr.employee'].search([('user_id','=',self.env.user.id)]).id)])[-1]
            }
        print(docargs)
        return docargs

class SALARYSLIPWIZ(models.TransientModel):
    _name = "hr.payslip.print"

    date_from = fields.Date()
    date_to = fields.Date()

    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from','date_to'])[0]
        return self._payslip_print(data)
    def _payslip_print(self,data):
        data['form'].update(self.read(['date_from','date_to'])[0])
        return self.env.ref('xperts_employee.report_payslip_inhert').report_action(self, data=data, config=False)

class SALARYCERTWIZ(models.TransientModel):
    _name = "hr.payslip.cert.print"

    bank = fields.Many2one('xperts.banks')

    def check_report(self):
        data = {}
        data['form'] = self.read(['bank'])[0]
        return self._payslip_cert_print(data)
    def _payslip_cert_print(self,data):
        data['form'].update(self.read(['bank'])[0])
        return self.env.ref('xperts_employee.report_payslip_cert_inhert').report_action(self, data=data, config=False)


class xperts_banks(models.Model):
    _name = 'xperts.banks'
    _description = 'Banks'
    name = fields.Char(string="Bank")
# class xperts_blood_groups(models.Model):
#     _name = 'xperts.blood.groups'
#     _description = 'Blood Groups'
#     name = fields.Char(string="Group")

class xperts_sponsor_details(models.Model):
    _name = 'xperts.sponsor.details'
    _description = 'Sponsor Details'
    name = fields.Char(string="Sponsor")

class xperts_payment_types(models.Model):
    _name = 'xperts.payment.type'
    _description = 'Payment Types'
    name = fields.Char(string="Payment")

# class xperts_bank_code(models.Model):
#     _name = 'xperts.bank.code'
#     _description = 'Bank Code'
#     name = fields.Char(string="Code")

class xperts_travel_class(models.Model):
    _name = 'xperts.travel.class'
    _description = 'Travel Class'
    name = fields.Char(string="Class")

class xperts_emp_status(models.Model):
    _name = 'xperts.emp.status'
    _description = 'Employee Status'
    name = fields.Char(string="Status")

class xperts_pay_group(models.Model):
    _name = 'xperts.pay.group'
    _description = 'Pay Groups'
    name = fields.Char(string="Group Name")

class xperts_project(models.Model):
    _name = 'xperts.project'
    _description = 'Project'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    def write(self, values):
        res = super(xperts_project,self).write(values)
        if self.service_id == self.env['product.product']:
            service_id = self.env['product.product'].sudo(1).create({
            'name':self.name,
            'sale_ok':True,
            'purchase_ok':True,
            'can_be_expensed':True,
            'type':'service',
            'company_id':self.company_id.id,
            })
            self.service_id = service_id.id
        return res
    @api.model
    def create(self, vals):
        res = super(xperts_project,self).create(vals)
        if res.service_id == self.env['product.product']:
            service_id = self.env['product.product'].sudo(1).create({
            'name':res.name,
            'sale_ok':True,
            'purchase_ok':True,
            'can_be_expensed':True,
            'type':'service',
            'company_id':res.company_id.id,
            })
            res.service_id = service_id.id
        return res
    service_id = fields.Many2one('product.product', string="Related Service")
    company_id = fields.Many2one('res.company')
    project_contract = fields.Many2one('xperts.project.contract')
    def _compute_members_ids(self):
        for this in self:
            members = self.env['hr.employee'].search([('project','=',self.id)])
            self.members_ids = members.ids
            for mem in self.members_ids:
                follower = self.env['mail.followers'].search([('res_model','=','xperts.project'),('res_id','=',self.id),('partner_id','=',mem.address_id.id)])
                if len(follower)>0:
                    pass
                else:
                    new_follower = self.env['mail.followers'].create({'res_model':'xperts.project','res_id':self.id,'partner_id':mem.address_id.id})

    name = fields.Char(string="Project Name")
    responsables_ids =  fields.Many2many('hr.employee','xperts_project_manager_employee_rel','project_id','employee_id')
    members_ids =  fields.Many2many('hr.employee','xperts_project_normal_employee_rel','project_id','employee_id',compute='_compute_members_ids')
class xperts_employee_category(models.Model):
    _name = 'xperts.emp.category'
    _description = 'Employee Category'
    name = fields.Char(string="Category Name")

class xperts_companies(models.Model):
    _name = 'xperts.company'
    _description = 'Company'
    name = fields.Char(string="Company")

class xperts_user_project(models.Model):
    _inherit = 'res.users'

    x_project = fields.Many2one(related='employee_id.project', store=True, required=False)

class xperts_payslip(models.Model):
    _inherit = 'hr.payslip'
    bank = fields.Many2one('xperts.banks')


    # @api.multi
    # def check_report(self):
    #     data = {}
    #     data['form'] = self.read(['',''])[0]
    #     return self._print_report(data)

    def print_salary_certificate(self):
        body = "<p>Dear " + self.employee_id.parent_id.name + "&nbsp;</p>"+"<p>Please Note That Your Employee" + self.employee_id.name + " Have Printed His Salary Certificate &nbsp;</p>"
        # body = "<p>Dear " + emp.name + "&nbsp;</p><p>Please Note That Your " + flag + " Have Been Expired And You Shoud Renew It Immediately&nbsp;</p> "
        mail = self.env['mail.mail'].create({'body_html':body,'email_to':self.employee_id.parent_id.work_email,})
        mail.send()
        return self.env.ref('xperts_employee.payslip_salary_certificate').report_action(self)

# class xperts_(models.Model):
#     _name = 'xperts.bank'
#
#     bank = fields.Many2one(string="Bank")


# class xperts_(models.Model):
#     _name = 'xperts.'
#     _description = ''
#     name = fields.Char(string="")
#
# class xperts_(models.Model):
#     _name = 'xperts.'
#     _description = ''
#     name = fields.Char(string="")

class xperts_employee(models.Model):
    _inherit = 'hr.employee'

    def check_expiaries(self):
        health_card_expairation_date_employees = self.env['hr.employee'].search([('health_card_expairation_date','<',datetime.datetime.now().date())])
        if health_card_expairation_date_employees:
            self.send_mail(health_card_expairation_date_employees ,"Health Card Expairation")
        haad_expairy_date_employees = self.env['hr.employee'].search([('haad_expairy_date','<',datetime.datetime.now().date())])
        if haad_expairy_date_employees:
            self.send_mail(haad_expairy_date_employees ,"Haad Expairy Date")
        marine_medical_expairy_date_employees = self.env['hr.employee'].search([('marine_medical_expairy_date','<',datetime.datetime.now().date())])
        if marine_medical_expairy_date_employees:
            self.send_mail(marine_medical_expairy_date_employees ,"Marine Medical Expairy Date")
        marine_coc_expairy_date_employees = self.env['hr.employee'].search([('marine_coc_expairy_date','<',datetime.datetime.now().date())])
        if marine_coc_expairy_date_employees:
            self.send_mail(marine_coc_expairy_date_employees ,"Marine Coc Expairy Date")
        fta_card_expairy_date_employees = self.env['hr.employee'].search([('fta_card_expairy_date','<',datetime.datetime.now().date())])
        if fta_card_expairy_date_employees:
            self.send_mail(fta_card_expairy_date_employees ,"Fta Card Expairy Date")
        armed_force_expairy_date_employees = self.env['hr.employee'].search([('armed_force_expairy_date','<',datetime.datetime.now().date())])
        if armed_force_expairy_date_employees:
            self.send_mail(armed_force_expairy_date_employees ,"Armed Force Expairy Date")
        eirs_car_plates_expairy_date_employees = self.env['hr.employee'].search([('eirs_car_plates_expairy_date','<',datetime.datetime.now().date())])
        if eirs_car_plates_expairy_date_employees:
            self.send_mail(eirs_car_plates_expairy_date_employees ,"Eirs Car Plates Expairy Date")
        trade_license_expiary_date_employees = self.env['hr.employee'].search([('trade_license_expiary_date','<',datetime.datetime.now().date())])
        if trade_license_expiary_date_employees:
            self.send_mail(trade_license_expiary_date_employees ,"Trade License Expiary Date")
        emirates_id_expairy_date_employees = self.env['hr.employee'].search([('emirates_id_expairy_date','<',datetime.datetime.now().date())])
        if emirates_id_expairy_date_employees:
            self.send_mail(emirates_id_expairy_date_employees ,"Emirates Id Expairy Date")
        pass_expairy_date_2_employees = self.env['hr.employee'].search([('pass_expairy_date_2','<',datetime.datetime.now().date())])
        if pass_expairy_date_2_employees:
            self.send_mail(pass_expairy_date_2_employees ,"Pass Expairy Date 2")
        pass_expairy_date_3_employees = self.env['hr.employee'].search([('pass_expairy_date_3','<',datetime.datetime.now().date())])
        if pass_expairy_date_3_employees:
            self.send_mail(pass_expairy_date_3_employees ,"Pass Expairy Date 3")
        pass_expairy_date_4_employees = self.env['hr.employee'].search([('pass_expairy_date_4','<',datetime.datetime.now().date())])
        if pass_expairy_date_4_employees:
            self.send_mail(pass_expairy_date_4_employees ,"Pass Expairy Date 4")
        pass_expairy_date_1_employees = self.env['hr.employee'].search([('pass_expairy_date_1','<',datetime.datetime.now().date())])
        if pass_expairy_date_1_employees:
            self.send_mail(pass_expairy_date_1_employees ,"Pass Expairy Date 1")
        passport_expairation_employees = self.env['hr.employee'].search([('passport_expairation','<',datetime.datetime.now().date())])
        if passport_expairation_employees:
            self.send_mail(passport_expairation_employees ,"Passport Expairation")
        cicpa_off_shore_expairy_date_employees = self.env['hr.employee'].search([('cicpa_off_shore_expairy_date','<',datetime.datetime.now().date())])
        if cicpa_off_shore_expairy_date_employees:
            self.send_mail(cicpa_off_shore_expairy_date_employees ,"Cicpa Off Shore Expairy Date")
        cicpa_on_shore_expairy_date_employees = self.env['hr.employee'].search([('cicpa_on_shore_expairy_date','<',datetime.datetime.now().date())])
        if cicpa_on_shore_expairy_date_employees:
            self.send_mail(cicpa_on_shore_expairy_date_employees ,"Cicpa On Shore Expairy Date")
        adp_gate_pass_expairy_date_employees = self.env['hr.employee'].search([('adp_gate_pass_expairy_date','<',datetime.datetime.now().date())])
        if adp_gate_pass_expairy_date_employees:
            self.send_mail(adp_gate_pass_expairy_date_employees ,"Adp Gate Pass Expairy Date")
        adac_expairy_date_employees = self.env['hr.employee'].search([('adac_expairy_date','<',datetime.datetime.now().date())])
        if adac_expairy_date_employees:
            self.send_mail(adac_expairy_date_employees ,"Adac Expairy Date")
        optima_expairy_date_employees = self.env['hr.employee'].search([('optima_expairy_date','<',datetime.datetime.now().date())])
        if optima_expairy_date_employees:
            self.send_mail(optima_expairy_date_employees ,"Optima Expairy Date")

    def send_mail(self ,emp_list ,flag):
        for emp in emp_list:
            body = "<p>Dear " + emp.name + "&nbsp;</p>"+"<p>Please Note That Your " + flag + " Have Been Expired And You Shoud Renew It Immediately&nbsp;</p>"
    		# body = "<p>Dear " + emp.name + "&nbsp;</p><p>Please Note That Your " + flag + " Have Been Expired And You Shoud Renew It Immediately&nbsp;</p> "
            mail = self.env['mail.mail'].create({'body_html':body,'email_to':emp.work_email,})
            mail.send()

    @api.model
    def create(self, vals):
        print("************************************8")
        res = super(xperts_employee,self).create(vals)
        if res.internal_user == False and res.service_id == self.env['product.product']:
            service_id = self.env['product.product'].sudo(1).create({
            'name':res.name,
            'sale_ok':True,
            'purchase_ok':True,
            'can_be_expensed':True,
            'type':'service',
            'company_id':res.company_id.id,
            })
            res.service_id = service_id.id
        return res

    def write(self, values):
        res = super(xperts_employee,self).write(values)
        if self.internal_user == False and self.service_id == self.env['product.product']:
            service_id = self.env['product.product'].sudo(1).create({
            'name':self.name,
            'sale_ok':True,
            'purchase_ok':True,
            'can_be_expensed':True,
            'type':'service',
            'company_id':self.company_id.id,
            })
            self.service_id = service_id.id
        return res

    service_id = fields.Many2one('product.product',string="Related Service")

    #NEW
    employee_number = fields.Char("Employee Number")
    name_as_mohre = fields.Char("Full Name as per MOHRE")
    uae_mobile = fields.Char("UAE Mobile Number")
    home_contact = fields.Char("Home Country Contact Number")
    home_address_perm = fields.Char("Permeant/Home Country Address")
    sos_person = fields.Char("Emergency person Name")
    sos_contact = fields.Char("Emergency Contact")
    sos_phone = fields.Char("Emergency Phone")
    contry_origin = fields.Many2one('res.country',"Country of Origin Home Address")
    employee_dependents = fields.One2many('xperts.dependents','employee_id')
    offboarding = fields.Boolean(default=False)
    offboarding_date = fields.Date()
    offboarding_reason = fields.Many2one('xperts.offboarding.reasons')
    full_name_passport = fields.Char("Full Name as per Passport")





    # Health Page
    health_card_number = fields.Char()
    health_card_expairation_date = fields.Date()
    blood_group = fields.Selection([('A+','A+'),('B+','B+'),('O+','O+'),('AB+','AB+'),('A-','A-'),('B-','B-'),('O-','O-'),('AB-','AB-')],'Blood Group')
    pre_employment_medical = fields.Selection([('applicable','Applicable'),('not_applicable','Not Applicable')], srting="Medical")
    #Health Page New
    medical_insurance_co = fields.Many2one('xperts.company',"Company Name")
    medical_insurance_coverage = fields.Many2one('xperts.insurance.coverage',"Coverage Plan / Coverage Type")
    medical_insurance_plicy_no = fields.Char("Policy No")
    medical_insurance_cn = fields.Char("Card Number")
    medical_insurance_start = fields.Date("Start Date")
    medical_insurance_expiry = fields.Date("Expiry Date")
    pre_emp_medical_date = fields.Date("Medical issue date")
    pre_emp_medical_end = fields.Date("Medical end date")
    fitness_status = fields.Many2one('xperts.fitness.status',"Fitness Status")
    fitness_document = fields.Binary("Fitness Document")


    #Armed Page
    armed_force = fields.Char("Armed Force Permit Number")
    armed_force_expairy_date = fields.Date("Armed Force Expiry Date")
    fta_card = fields.Char("FTA Card Number")
    marine_coc = fields.Char("Marine COP Number")
    marine_medical = fields.Char()
    haad = fields.Char("HAAD License Number")
    haad_expairy_date = fields.Date("HAAD License Expiry Date")
    marine_medical_expairy_date = fields.Date()
    marine_coc_expairy_date = fields.Date("Marine COP Expiry Date")
    fta_card_expairy_date = fields.Date("FTA Card Expiry Date")
    #Armed Page NEw
    armed_force_issue_date = fields.Date("Armed Force Issue Date")
    fta_issue_date = fields.Date("FTA Card Issue Date")
    haad_issue_date = fields.Date("HAAD License Issue Date")
    marine_issue_date = fields.Date("Marine COP Issue Date")

    #Cicpa
    cicpa_on_shore = fields.Char("CICPA Onshore Number")
    cicpa_on_shore_expairy_date = fields.Date("CICPA Onshore Expiry Date")
    cicpa_off_shore = fields.Char("CICPA Offshore Number")
    cicpa_off_shore_expairy_date = fields.Date("CICPA Offshore Expiry Date")
    #Cicpa NEw
    cicpa_on_shore_issue_date = fields.Date("CICPA Onshore Issue Date")
    cicpa_off_shore_issue_date = fields.Date("CICPA Offshore Issue Date")
    cicpa_on_shore_card = fields.Date("CICPA Onshore Card Number")
    cicpa_off_shore_card = fields.Date("CICPA Offshore Card Number")
    #optima
    optima = fields.Char("Optima Card Number")
    optima_expairy_date = fields.Date("Optima Expiry Date")
    #optima new
    optima_issue_date = fields.Date("Optima Issue Date")
    #adac
    adac = fields.Char("ADAC Permit Number")
    adac_expairy_date = fields.Date("ADAC Expiry Date")
    #adac new
    adac_issue_date = fields.Date("ADAC Issue Date")
    #adp
    adp_gate_pass = fields.Char("ADP Gate Pass Number")
    adp_gate_pass_expairy_date = fields.Date("ADP Gate Pass Expiry Date")
    #adp new
    adp_issue_date = fields.Date("ADP Gate Pass Issue Date")
    #premit new
    client_management_approval = fields.Char("Client Management Approval")
    issue_date = fields.Date("Issue Date")
    expirt_date = fields.Date("Expiry Date")

    #Driving Page
    driving_licence_number = fields.Char()
    driving_licence_issue_place = fields.Many2one('res.country')
    driving_licence_expairation_date = fields.Date()
    trade_license = fields.Char()
    eirs_car_plates = fields.Char()
    eirs_car_plates_expairy_date = fields.Date()
    trade_license_expiary_date = fields.Date()
    travel_class = fields.Many2one('xperts.travel.class')
    last_air_ticket_date = fields.Date()

    #Allowances
    basic_act = fields.Float("Basic Salary")
    hra_act = fields.Float()
    transport_act = fields.Float("Transportation Allowance")
    other_allowance_act = fields.Float("Other Allowance")
    monthly_earning_act = fields.Float("Total Monthly Earning")
    food_allowance_act = fields.Float("Food Allowance")
    telephone_act = fields.Float("Telephone Allowance")
    fuel_act = fields.Float("Fuel Allowance")

    #Leaves
    sick_leave = fields.Float()
    maternity_leave = fields.Float()
    haj_leave = fields.Float()
    annual_leave = fields.Float()
    paternity_leave = fields.Float()
    negative_leave = fields.Float()
    sick_leave_bf = fields.Float()
    maternity_leave_bf = fields.Float()
    haj_leave_bf = fields.Float()
    unpaid_leave_bf = fields.Float()
    annual_leave_bf = fields.Float()
    paternity_leave_bf = fields.Float()
    ctc = fields.Float()
    lop_days = fields.Float()
    probation_period = fields.Float()
    notice_period = fields.Float()
    #NEW
    rational = fields.Float("Rotational Leave")

    #Accounts
    salary_account = fields.Many2one('account.account')
    emp_account = fields.Many2one('account.account',string="Employee Account")
    acc_no = fields.Many2one('account.account',string="Account Number")
    bank_country = fields.Many2one('res.country',"Bank Country")
    routing_bank_code = fields.Char("Routing Bank Code")

    #Personal
    arabic_name = fields.Char()
    home_country = fields.Many2one('res.country')
    emirates_id_number = fields.Char()
    emirates_id_card_number = fields.Char()
    emirates_id_expairy_date = fields.Date()

    #Visa
    # visa_designation = fields.Char()
    visa_issue_place = fields.Many2one('res.country')
    visa_issue_date = fields.Date()
    visa_company = fields.Many2one('xperts.company')

    #Passport
    swift_code = fields.Char("Swift Code")
    pass_expairy_date_2 = fields.Date()
    pass_expairy_date_3 = fields.Date()
    pass_expairy_date_4 = fields.Date()
    pass_expairy_date_1 = fields.Date()
    passport_expairation = fields.Date()
    passport_issue_date = fields.Date('Passport Issue Date')
    passport_issue_place = fields.Many2one('res.country')
    #New
    place_of_birth = fields.Char()
    country_of_birth = fields.Many2one('res.country')
    eid_issue_date = fields.Date("EID Issue Date")
    work_permit_number = fields.Char()
    uid_no = fields.Char("UID No.")
    #General
    internal_user = fields.Boolean()
    code = fields.Char()
    revision_date = fields.Date()
    applicable_date = fields.Date()
    date_of_joining = fields.Date("Hired Date")
    # designation = fields.Char()
    project = fields.Many2one('xperts.project')
    job_visa = fields.Many2one('hr.job',string="Position as per Offer")
    job_id = fields.Many2one('hr.job',string="Job Position On Project")
    position = fields.Many2one('hr.job',string="Position")
    reporting_to = fields.Many2one('res.partner')
    emp_category = fields.Many2one('xperts.emp.category',string="Employee Category")
    pay_group = fields.Many2one('xperts.pay.group',"Pay Group")
    currency = fields.Many2one('res.currency',"Currency")
    emp_status = fields.Many2one('xperts.emp.status',string="Employee Status",required=False)
    sponsor_details = fields.Many2one('xperts.sponsor.details')
    payment_type = fields.Many2one('xperts.payment.type',"Payment Type")
    branch = fields.Char()
    labor_no = fields.Char()
    labor_card_no = fields.Char()
    labor_card_expiry = fields.Date()
    place = fields.Char()
    father_name = fields.Char()
    mother_name = fields.Char()
    international_phone= fields.Char()
    xperts_company = fields.Many2one('xperts.company', string="Company")
    company_id = fields.Many2one('res.company', string="Internal Company")
    #New
    company_assignment = fields.Char("Company Assignment")
    start_work_order = fields.Date("Start Date of Work Order")
    end_work_order = fields.Date("Expiry Date of Work Order ")
    airticket_date_eligibilty = fields.Boolean("Eligibility of Air Ticket Date")
    custody_item_1 = fields.Char("Custody Item 1")
    custody_item_2 = fields.Char("Custody Item 2")
    custody_item_3 = fields.Char("Custody Item 3")
    custody_item_4 = fields.Char("Custody Item 4")
    #Others
    permenant_residance_ic_no = fields.Char()
    service_duration = fields.Char()

    # NEW
    housing_allowance = fields.Float("Housing Allowance")
    cost_living_allowance= fields.Float("Cost of living Allowance")
    social_allowance= fields.Float("Social Allowance")
    airfare_allowance= fields.Float("Airfare Allowance")
    remote_allowance= fields.Float("Remote Allowance")
    mawaqif_allowance= fields.Float("Mawaqif Allowane")

    bank_name = fields.Many2one('xperts.banks',"Bank Name")
    bank_account_number= fields.Char("Bank Account Number")
    iban = fields.Char("IBAN")

    increment_1 = fields.Float("Increment 1")
    effective_date_1 = fields.Date("Effective Date")
    increment_2 = fields.Float("Increment 2")
    effective_date_2 = fields.Float("Effective Date")


class accountgroup(models.Model):
    _inherit = 'account.account'

    def change_group(self):
        groups = self.env['account.group'].search([('parent_id','!=',False)])
        print(len(groups))
        for group in groups:
            like_prefix = group.code_prefix[0:5]+'%'
            print(like_prefix)
            accounts = self.env['account.account'].search([('code','like',like_prefix)])
            for account in accounts:
                account.group_id = group.id


class xperts_insurance_coverage(models.Model):
    _name = 'xperts.insurance.coverage'
    _description = 'Insurance Coverage'
    name = fields.Char(string="Coverage Play / Coverage Type")

class xperts_fitness_status(models.Model):
    _name = 'xperts.fitness.status'
    _description = 'Fitness Status'
    name = fields.Char(string="Status")

class xperts_fitness_status(models.Model):
    _name = 'xperts.dependent_1'
    _description = 'Fitness Status'
    name = fields.Char(string="Status")


class xperts_mail(models.TransientModel):
    _inherit = 'mail.compose.message'

    project = fields.Many2one('xperts.project')

    @api.onchange('project')
    def recepients_project(self):
        if self.project:
            list_partners_to_mail = []
            for emp in self.project.members_ids:
                if emp and emp.work_email:
                    partner = self.env['res.partner'].search([('email','=',emp.work_email)])
                    if partner:
                        list_partners_to_mail.append(partner[0].id)
            self.partner_ids = [(6,0,list_partners_to_mail)]


class xperts_dependents(models.Model):
    _name = 'xperts.dependents'

    name = fields.Char('Dependent  Name')
    relation = fields.Char('Relation')
    dob = fields.Date('Date of Birth')
    visa_num = fields.Binary('Visa Number')
    passport_num = fields.Binary('Passport Number')
    eid_no = fields.Binary('Emirates ID Number')
    photo = fields.Binary('Photo')
    prev_visa = fields.Binary('Previous visa')
    coc = fields.Binary('COC')
    birth_cert = fields.Binary('Birth Certificate (newborn)')
    employee_id = fields.Many2one('hr.employee')
