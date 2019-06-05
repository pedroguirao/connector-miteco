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


class EnviaMapama(models.Model):
    _name = 'mapamas'
    _description='Enviar a mapama'
        
    x_di_id = fields.Many2one('x_dis')
    x_name = fields.Char('Nombre DI')
    x_id_mapama = fields.Char('Id Mapama',help='Identificador en Servicio Mapama')
    x_estado = fields.Char('Estado',help='Enviado, Error, Pendiente',default='Pendiente')
    x_fecha_creacion = fields.Date('fecha de creación')
    x_usuario_mapama = fields.Char('Usuario Servicio',help='Usuario que realiza el envío al servicio Mapama')
    x_codigo_estado = fields.Char('Código de Estado',help='Código de error o de operación satisfactoria')
    x_mensaje_estado = fields.Char('Mensaje de Estado',help='Mensaje devuelto por el Servidor Mapama')
    x_debug = fields.Text()
    #x_name = fields.Char(String='Nombre DI') 
        
    
    @api.one
    def send2mapama(self):
        #
        #self.x_estado = self.x_di_id.x_secuencia_di
        self.x_name = self.x_di_id.x_codigo_di
        
        ############################################
        #  Usuario del servicio Mapama que realiza #
        #  el envío del Di                         #
        ############################################
        
        user = self.x_di_id.x_mapama_usuario_id
        self.x_usuario_mapama = user
        password = self.x_di_id.x_mapama_pw_id
        
        user = '34785211B'
        password = 'dparis'
        #############################################
        
        # condicional si fecha == False
        
        
        ############## Sender Mapama / Operador de Traslado #############################

        sender_wasteERAEE = {
            'senderType': self.x_di_id.x_gestor_tipocentro_codigo_id,
            'caCode': self.x_di_id.x_operador_ccaa_codigo_ine_id,
            'deliveryDate': self.x_di_id.x_fdi_inicio_id,
            'leavingDate':self.x_di_id.x_fdi_entrega_id,
            'operationProcess': self.x_di_id.x_gestor_tratamiento_id.x_name,
            'entryCode': "",
            'registeredInfoDataType': {
                'authorizationIdNumber': self.x_di_id.x_operador_autorizacion_id.x_name,
                'nima': self.x_di_id.x_operador_nima_id,
                'nif': self.x_di_id.x_operador_nif_mapama_id,
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
                     'quantity': '10',
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
        
        if self.x_di_id.x_trans1_autorizacion != False:
            trasporter_wasteERAEE = {
                'transporter': {
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
                        'registeredInfoDataType': {
                        'authotizationIdNumber': self.x_di_id.x_trans1_autorizacion,
                        'nima': self.x_di_id.x_trans1_nima_id,  #3020133042,
                        'nif': self.x_di_id.x_trans1_nif_mapama_id,  #B73862468,
                        'authorizationCode': self.x_di_id.x_trans1_tipo_mapama_id
                    }},
            }
        else:
            trasporter_wasteERAEE = {
                'transporter': {
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
        
        self.x_debug = str(wasteERAEE)
        
        self.x_estado = "Error"
        session = Session()
        self.x_estado = "Error 1"
        session.auth = HTTPBasicAuth(user, password)
        self.x_estado = "Error 2"
        client : Client = Client('https://preservicio.mapama.gob.es/raee-service/soap-raee/soapRaee.wsdl',transport=Transport(session=session))
        self.x_estado = client.service.sendWasteEntries(wasteERAEE)
        
        #var = client.service.sendWasteEntries(wasteERAEE)
       
        #self.x_estado = "Error 4"
        #insertado=var['success']
        #self.x_mensaje_estado = var['error'][0]['errorMessage']
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
        

       



        
        
        



