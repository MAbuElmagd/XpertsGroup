# -*- coding: utf-8 -*-

from odoo import models, fields, api


class faq(models.Model):
    _name = 'faq.faq'
    _description = 'faq.faq'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    question=fields.Char(string="Question",required=True)
    solution=fields.Text(string="Solution",required=True)
    video = fields.Char(string="Video", default='https://www.youtube.com')
    attachment=fields.Binary()
    tags=fields.Many2many('faq.tag')
    category=fields.Many2one('faq.category')
class tag(models.Model):
    _name= 'faq.tag'

    name=fields.Char(string="Name",required=True)
class Category(models.Model):
    _name= 'faq.category'

    name=fields.Char(string="Name",required=True)
    questions=fields.One2many('faq.faq','question')
