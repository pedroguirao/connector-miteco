# -*- coding: utf-8 -*-

import logging
#import time
#import urllib.request
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from requests import Session
from zeep import Client
from zeep.transports import Transport
#from zeep import xsd
#from datetime import datetime
from odoo import api, fields, models 
from odoo.exceptions import ValidationError
from odoo.osv import osv


class EnviaMapama(models.Model):
    _name = 'mapamas'
    _description='Enviar a mapama'
        
    x_di_id = fields.Many2one('x_dis',string='DI para enviar')
    x_name = fields.Char('Nombre DI')
    x_id_mapama = fields.Char('Id Mapama',help='Identificador en Servicio Mapama')
    x_estado = fields.Char('Estado',help='Enviado, Error, Pendiente',default='Pendiente')
    x_fecha_creacion = fields.Date('Fecha Mapama')
    x_usuario_mapama = fields.Char('Usuario Servicio',help='Usuario que realiza el envío al servicio Mapama')
    x_codigo_estado = fields.Char('Código de Estado',help='Código de error o de operación satisfactoria')
    x_empresa = fields.Char('Empresa',help='Empresa que envía el DI')
    x_debug = fields.Text('Respuesta Servidor')
    #x_name = fields.Char(String='Nombre DI') 
            
    @api.constrains('x_di_id')
    def nombradi(self):
        self.x_name = self.x_di_id.x_codigo_di
        if self.x_di_id.x_estado != False:
            self.x_estado = self.x_di_id.x_estado        
        
    
    @api.multi
    def send2mapama(self): 
        
        #self.x_estado = self.x_di_id.x_secuencia_di
        
        ############ Tomar empresa desde la cual envía el usuario registrado ###########
        company = self.env['res.company']._company_default_get('mapamas')
        self.x_empresa = company.partner_id.name
        
        transporter_origin = 'nationalTransporter'
        
        ############################################
        #  Usuario del servicio Mapama que realiza #
        #  el envío del Di                         #
        ############################################
        
        #user = self.x_di_id.x_mapama_usuario_id
        #self.x_usuario_mapama = user
        #password = self.x_di_id.x_mapama_pw_id
        
        user = company.partner_id.x_mapama_usuario
        self.x_usuario_mapama = user
        password = company.partner_id.x_mapama_pw
        
        #user = '34785211B'
        #password = 'dparis'
        #############################################
        
        # condicional si fecha == False
        
        
        ############## Sender Mapama / Operador de Traslado #############################

        #sender_wasteERAEE = {
        #    'senderType': self.x_di_id.x_gestor_tipocentro_id.x_codigo,
        #    'caCode': self.x_di_id.x_operador_ccaa_codigo_ine_id,
        #    'deliveryDate': self.x_di_id.x_fdi_inicio_id,
        #    'leavingDate':self.x_di_id.x_fdi_entrega_id,
        #    'operationProcess': self.x_di_id.x_gestor_tratamiento_id.x_name,
        #    'entryCode': "",
        #    'registeredInfoDataType': {
        #        'authorizationIdNumber': self.x_di_id.x_operador_autorizacion_id.x_name,
        #        'nima': self.x_di_id.x_operador_nima_id,
        #        'nif': self.x_di_id.x_operador_nif_mapama_id,
        #        'authorizationCode': self.x_di_id.x_operador_tipo_mapama_id,
        #    }
        #
        #}
        sender_wasteERAEE = {
            'senderType': company.partner_id.x_tipocentro_id.x_codigo,
            'caCode': self.x_di_id.x_operador_ccaa_codigo_ine_id,
            'deliveryDate': self.x_di_id.x_fdi_inicio_id,
            'leavingDate':self.x_di_id.x_fdi_entrega_id,
            'operationProcess': self.x_di_id.x_gestor_tratamiento_id.x_name,
            'entryCode': "",
            'registeredInfoDataType': {
                'authorizationIdNumber': self.x_di_id.x_operador_autorizacion_id.x_name,
                'nima': company.partner_id.x_nima_mapama,
                'nif': company.partner_id.x_nif_mapama,
                'authorizationCode': self.x_di_id.x_operador_tipo_mapama_id,
            }
        
        }
        
        
        
        ############# DepositoryData Mapama  / Productor ###################################
        
        
        if self.x_di_id.x_productor_autorizacion_id != False:
            depositary_wasteERAEE = {
                'depositaryData': {
                    'nif': self.x_di_id.x_productor_nif_mapama_id,
                    # 'name':  "",
                    # 'surname1':  "",
                    'reason': self.x_di_id.x_productor_id.name,
                    'caCode': self.x_di_id.x_productor_ccaa_codigo_ine_id,
                    'depositaryRAEEType': self.x_di_id.x_productor_tipodepositario_codigo_id,
                    'originOperationProcess':self.x_di_id.x_productor_tratamiento_id.x_name,
                    'address': {
                        # 'countryCode':
                        'provinceCode': self.x_di_id.x_productor_provincia_codigo_ine_id,
                        # 'municipalityCode':
                     # 'cp':
                        'address': self.x_di_id.x_productor_direccion_id,
                        # 'codVial':
                    },
                    'registeredInfoDataType': {
                     'authorizationIdNumber': self.x_di_id.x_productor_autorizacion_id,
                     'nima': self.x_di_id.x_productor_nima_id,
                     'nif': self.x_di_id.x_productor_nif_mapama_id,
                     'authorizationCode': self.x_di_id.x_productor_tipo_mapama_id,
                    }},

            }

        else:
            depositary_wasteERAEE = {
        
                'depositaryData': {
                    'nif': self.x_di_id.x_productor_nif_mapama_id,
                    # 'name':
                    # 'surname1':
                    'reason': self.x_di_id.x_productor_id.name,
                    'caCode': self.x_di_id.x_productor_ccaa_codigo_ine_id,
                    'depositaryRAEEType': self.x_di_id.x_productor_tipodepositario_codigo_id,
                    'originOperationProcess':self.x_di_id.x_productor_tratamiento_id.x_name,
                    'address': {
                        # 'countryCode':
                        'provinceCode': self.x_di_id.x_productor_provincia_codigo_ine_id,
                        # 'municipalityCode':
                        # 'cp':
                        'address': self.x_di_id.x_productor_direccion_id,
                        # 'codVial':
                    },
                },
            }
            
            
        ############## Mapama DeviceData / Características del residuo #############################
        
        device_wasteERAEE = {
            'deviceData': {
                 #'LERCode': '20013652',
                 'LERCode': self.x_di_id.x_ler_codigo_mapama_id,
                 'units': '10',
                 # 'deviceType': deviceType,
                 # 'tippedOver': tippedOver,
                 #'use': Di[0]['x_ler_origen_id'],
                 # 'raeeReference':raeeReference,   # No si es alta
                 # 'containerReference':containerReference,
                 #  'brand':{
                 #      'brand':brand,
                 #      'units':units_brand},
                 'quantity': {
                     'quantity':self.x_di_id.x_pesoneto,
                     'units': '10'},
                 # 'serialNumber':serialNumber,
                 'observations': '',
    
                  # 'incidence': {
                    #    'incidenceType': '01',
                 #    'units':'0'  },
                 # 'otherBrand':{
                 #    'brandName':'',
                 #    'units':''}
                },
        }
        
        ###################### Transporter / Transportista #################################
        if transporter_origin == 'nationalTransporter':
            if self.x_di_id.x_trans1_autorizacion != False:
              
                trasporter_wasteERAEE = {
                    'nationalTransporter': {
                        'nif': self.x_di_id.x_trans1_nif_mapama_id,
                        # 'name':'',
                        # 'surname1':'',
                        'reason': self.x_di_id.x_trans1_id.name,
                        'caCode': self.x_di_id.x_trans1_ccaa_codigo_ine_id,
                        # 'countryCode':'724',
                        # 'provinceCode':'30',
                        # 'municipalityCode':'400019',
                        # 'cp':'30203',
                        # 'address':'calle',
                        # 'codVial':'001'
                        #'registeredInfoDataType': {
                        'authotizationIdNumber': self.x_di_id.x_trans1_autorizacion.x_name,
                        'nima': self.x_di_id.x_trans1_nima_id,  #3020133042,
                        'nif': self.x_di_id.x_trans1_nif_mapama_id,  #B73862468,
                        'authorizationCode': self.x_di_id.x_trans1_tipo_mapama_id
                       # }
                    },
                }
            else:
                trasporter_wasteERAEE = {
                   
                    'nationalTransporter': {
                        'nif': self.x_di_id.x_trans1_nif_mapama_id,
                        # 'name':'',
                        # 'surname1':'',
                        'reason': self.x_di_id.x_trans1_id.name,
                        'caCode': self.x_di_id.x_trans1_ccaa_codigo_ine_id,
                        'address': {
                            # 'countryCode':'724',
                            # 'provinceCode':'30',
                            # 'municipalityCode':'400019',
                            # 'cp':'30203',
                            # 'address':'calle',
                            # 'codVial':'001'
                        },
                      },
                }
        else: 
           
            trasporter_wasteERAEE = {
                'foreignTransporter': {
                    'countryCode':'',
                    'name':'',
                    'reason':'' ,
                    'surname':'',
                },    
            }
            
            
        #########################DatosRecogida##########################################

        if self.x_di_id.x_productor_gestionadoporscrap == True:
            recogida_wasteERAEE = {
                'collectionRAEEData': {
                    'receiver': '02',
                    # 'referenceNumber':referenceNumber_recogida,
                    # 'assigmenOfficeId':assignmentOfficeId_recogida,
                    # 'responsabilitySystemData':{
                    #   'authorizationIdNumber':authorizationIdNumber_recogida,
                    #   'nima':nima_recogida,
                    #   'nif':nif_recogida,
                    #   'authorizationCode':authorizationCode_recogida},
                    'sigCode':self.x_di_id.x_productor_codmapamascrap_id},
                # 'deliveryNotes':deliveryNotes,
                'identifierDI': self.x_di_id.x_codigo_di}
        


        else:
            recogida_wasteERAEE = {
                'collectionRAEEData': {
                    'receiver': '03',
                    # 'referenceNumber':referenceNumber_recogida,
                    # 'assigmenOfficeId':assignmentOfficeId_recogida,
                    'responsabilitySystemData': {
                        'authorizationIdNumber': self.x_di_id.x_productor_autorizacion_id,
                        'nima':self.x_di_id.x_productor_nima_id,
                        'nif': self.x_di_id.x_productor_nif_mapama_id,
                        'authorizationCode': self.x_di_id.x_productor_tipo_mapama_id, },

                    # 'sigCode':

                },
                # 'deliveryNotes':deliveryNotes,
                'identifierDI': self.x_di_id.x_codigo_di}
            
        
        wasteERAEE = {**sender_wasteERAEE, **depositary_wasteERAEE, **device_wasteERAEE, **trasporter_wasteERAEE, **recogida_wasteERAEE}
        
        #self.x_debug = str(wasteERAEE)
        
        session = Session()
        session.auth = HTTPBasicAuth(user, password)
        
        #self.x_debug = client.service.sendWasteEntries(wasteERAEE)
        
        try:
            client : Client = Client('https://preservicio.mapama.gob.es/raee-service/soap-raee/soapRaee.wsdl',transport=Transport(session=session))
            srv_response = client.service.sendWasteEntries(wasteERAEE)
            
        except Exception as e:
            raise ValidationError('El servidor a rechazado la comunicación. Revise el Usuario y Contraseña')
           
            
        self.x_debug = ''
        if srv_response['success'] == False:
            self.x_estado = "Error"
            errores=srv_response['error']
            for l in range(len(errores)):
                self.x_debug =self.x_debug + "\n" + str(errores[l]['errorMessage'])
            self.x_di_id.x_estado = 'errorenvio'
        else:
            self.x_estado = "Enviado"
            self.x_debug =srv_response['error']
            self.x_di_id.x_estado = 'enviado'
            self.x_id_mapama = srv_response['entryResponse']
        
        return 0        
        #enviado = recibe2mapama(var)

        ################# INSERTAR RESPUESTA EN ODOO ################
        
        #@api.one
        #def recibe2mapama(self, data):
        
        #    insertado=var['success']
        
        #    if insertado != False:
              #  codigos = var['entryResponse']
              #  recibo_mapama = codigos[0]['entryCode']
              #  
              #      'x_estado': "enviado",
              #      'x_id_mapama': recibo_mapama
              #
              #  print (codigos[0]['entryCode'])
    
        #    else:
        #        self.x_mensaje_estado = var['error'][0]['errorMessage']
        #        self.x_estado = "Error"
        #        self.x_codigo_estado = var['error'][0]['errorCode']    
        
        #return 1
        
        
    @api.multi
    def check_di(self):
        company = self.env['res.company']._company_default_get('mapamas')
        if company.partner_id.x_mapama_usuario == False or company.partner_id.x_mapama_pw == False:
          raise osv.except_osv(('Usuario plataforma'), ('Usuario o Contraseña para el servicio no definida'))
        if company.partner_id.x_tipocentro_id.x_codigo == False or company.partner_id.x_nima_mapama == False:
          raise osv.except_osv(('Tipo de Centro y NIMA'), ('Tipo de Centro o NIMA no deffinido'))
        if self.x_di_id.x_operador_autorizacion_id.x_name == False or self.x_di_id.x_operador_tipo_mapama_id == False:
          raise osv.except_osv(('Autorización'), ('Código o Número de autorización deffinido'))
        
        
        result = self.send2mapama()
        if result!=0:
            self.x_estado="El servidor ha rechazado la comuniación"
            

       



        
        
        



