# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    if int(auth.user.id) == 8 :
        redirect(URL(superindex)) 
    cate=db(db.cattable.id>0).select()
    posts=db(db.post.id>0).select(orderby=~db.post.rating)
    comments=db(db.com.id>0).select(orderby=db.com.tstamp)
    return locals()
    #return dict(posts,message=T('Hello World'))

def superindex():
    cate=db(db.cattable.id>0).select()
    posts=db(db.post.id>0).select(orderby=~db.post.rating)
    comments=db(db.com.id>0).select(orderby=db.com.tstamp)
    return locals()

def superhome():
    arg=request.vars.a
    cate=db(db.cattable.id>0).select()
    posts=db(db.post.id>0).select(orderby=~db.post.rating)
    comments=db(db.com.id>0).select(orderby=db.com.tstamp)
    return locals()
    
def newcat():
    form=SQLFORM(db.cattable)
    if form.process().accepted:
        response.flash="form accepted"
    elif form.errors:
        response.flash="Errors in form"
    return dict(form=form)
     
@auth.requires_login()      
def home():
    arg=request.vars.a
    cate=db(db.cattable.id>0).select()
    posts=db(db.post.id>0).select(orderby=~db.post.rating)
    comments=db(db.com.id>0).select(orderby=db.com.tstamp)
    return locals()
    
@auth.requires_login()    
def deletepost():
    argid=request.vars.a
    db(db.post.id==argid).delete()
    session.flash = 'Post deleted'
    if int(auth.user.id) == 8 :
        redirect(URL(superindex)) 
    redirect(URL(index)) 
         
@auth.requires_login()
def editpost():
    argid=request.vars.a
    if int(auth.user.id) == 8 :
       crud.settings.update_next = URL('superindex')
    else :
        crud.settings.update_next = URL('index')
    return dict(form=crud.update(db.post, request.vars.a))
       
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@auth.requires_login()
def newpost():
    form=SQLFORM(db.post)
    db.post.authorID.default=auth.user_id
    if form.process().accepted:
        response.flash="form accepted"
    elif form.errors:
        response.flash="Errors in form"
    return dict(form=form) 

@auth.requires_login()
def newcomment():
    p=int(request.vars.a)
    db.com.authID.default=auth.user_id
    db.com.postID.default=p
    r=db(auth.user_id==db.auth_user.id).select(db.auth_user.first_name,db.auth_user.last_name)
    db.com.authname.default=r[0]['first_name']+' '+r[0]['last_name']
    form=SQLFORM(db.com).process(next=URL('default','index'))
    if form.process().accepted:
        response.flash="form accepted"
    elif form.errors:
        response.flash="Errors in form"
    return dict(form=form) 

@auth.requires_login()
def upvote():
     p=int(request.vars.a)
     flag=0
     down=0
     r=db(db.ltable.id>0).select()
     rd=db(db.dtable.id>0).select()
     for i in r:
        if int(i['postID']) == p : 
            if int(i['upvoter']) == auth.user.id:
                          flag=1
                          
     for i in rd:
        if int(i['postID']) == p : 
            if int(i['downvoter']) == auth.user.id:
                          down=1
                          
     if flag == 0 and down == 0 :
         db(db.post.id == p).update(rating = db.post.rating + 5)
         db.ltable.insert(upvoter=auth.user.id,postID=p)
         session.flash = 'Upvoted successfully'
         
     if flag == 0 :
         if down == 1:
             db(db.post.id == p).update(rating = db.post.rating + 8)
             db.ltable.insert(upvoter=auth.user.id,postID=p)
             db(db.dtable.downvoter == auth.user.id).delete()
             session.flash = 'Upvoted - Nullified Downvote'
             
     if flag == 1:
            db(db.post.id == p).update(rating = db.post.rating - 5)
            db(db.ltable.upvoter == auth.user.id).delete()
            session.flash = 'Upvoted nullified'
         
     
    
     if int(auth.user.id) == 8 :
        redirect(URL(superindex)) 
        
     redirect(URL(index))    

@auth.requires_login()    
def removeacc():
    if int(auth.user.id) != 8:
        redirect(URL(index))
    arg=int(request.vars.a)
    db(db.auth_user.id == arg).delete()
    db(db.post.authorID == arg).delete() 
    db(db.ltable.upvoter == arg).delete()
    db(db.dtable.downvoter == arg).delete()
    db(db.com.authID == arg).delete()
    session.flash = 'Account deleted !'
    redirect(URL(superindex))

@auth.requires_login()   
def delusr():
    if int(auth.user.id) != 8:
        redirect(URL(index))
    x=db(db.auth_user.id > 0).select()
    return locals()
    
    
@auth.requires_login()   
def downvote():
     p=int(request.vars.a)
     flag=0
     r=db(db.dtable.id>0).select()
     rl=db(db.ltable.id>0).select()
     up=0
     
     for i in r:
        if int(i['postID']) == p : 
            if int(i['downvoter']) == auth.user.id:
                          flag=1
     for i in rl:
        if int(i['postID']) == p : 
            if int(i['upvoter']) == auth.user.id:
                          up=1
                          
     if flag == 0 and up==0 :
         db(db.post.id == p).update(rating = db.post.rating - 3)
         db.dtable.insert(downvoter=auth.user.id,postID=p)
         session.flash = 'Downvoted successfully'
     
     if flag == 0 and up==1 :  
             db(db.post.id == p).update(rating = db.post.rating - 8)
             db.dtable.insert(downvoter=auth.user.id,postID=p)
             db(db.ltable.upvoter == auth.user.id).delete()
             session.flash = 'Downvoted - Nullified Upvote'
     
     if flag == 1:
            db(db.post.id == p).update(rating = db.post.rating + 3)
            db(db.dtable.downvoter == auth.user.id).delete()
            session.flash = 'Nullified downvote'
             
     if int(auth.user.id) == 8 :
          redirect(URL(superindex)) 
     redirect(URL(index))  
     
     
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
