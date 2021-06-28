from django.db import models

# Create your models here.

class planet_info(models.Model):
    psid = models.CharField(max_length=6)
    psname = models.CharField(max_length=6)
    pvalue = models.IntegerField()
    pspeed_max = models.IntegerField()
    pflight_max = models.IntegerField()
    pcombat_radius = models.IntegerField()
    pload_max = models.IntegerField()
    plongitude = models.FloatField()
    platitude = models.FloatField()

class radar_info(models.Model):
    rsname = models.IntegerField()
    rtype = models.CharField(max_length=7)
    rop_band = models.IntegerField()
    rpulse_width = models.IntegerField()
    rantenna_gain = models.IntegerField()
    rpulse_freq = models.IntegerField()
    rtrans_power = models.IntegerField()
    rradius_max = models.IntegerField()
    rdist_max = models.IntegerField()
    rdist_min = models.IntegerField()
    rpos_accuracy = models.IntegerField()
    ranti_interference = models.FloatField()

class transfer(models.Model):
    resource_name = models.CharField(max_length=10)
    classes = models.IntegerField()
    model = models.IntegerField()

class classes(models.Model):
    class_name = models.IntegerField()
    number = models.IntegerField()

class model(models.Model):
    model_name = models.IntegerField()
    class_name = models.IntegerField()
    number = models.IntegerField()

class arm_info(models.Model):
    asname = models.IntegerField()
    atype = models.CharField(max_length=7)
    aspeed = models.IntegerField()
    akill_radius = models.IntegerField()
    ahit_rate = models.FloatField()
    aguide_accuracy = models.IntegerField()
    ahit_accuracy = models.IntegerField()
    aattack_distmax = models.IntegerField()
    aattack_distmin = models.IntegerField()
    afight_heightmax = models.IntegerField()
    afight_heightmin = models.IntegerField()
    areliability = models.FloatField()
    aanti_interference = models.FloatField()
    astealth = models.FloatField()
    areaction_time = models.FloatField()
    apayload = models.FloatField()
    aguide_type = models.IntegerField()
    avalue = models.IntegerField()

class compute_info(models.Model):
    csname = models.IntegerField()
    ctype = models.CharField(max_length=7)
    caccuracy = models.IntegerField()



