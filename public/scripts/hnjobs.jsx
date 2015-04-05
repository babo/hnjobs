var

DislikeButton = React.createClass({
    handleCommentSubmit: function (comment) {
        var comments = this.state.data,
            newComments = comments.concat([comment]);
        this.setState({data: newComments});

    },
    handleClick: function () {
        var url=this.props.url + '/hide/' + this.props.id;

        $.ajax({
            url: url,
            type: 'DELETE',
            success: function (data) {
                if (data.success === true) {
                    this.props.hide_cb(this.props.id);
                } else {
                    console.error('Failed to hide ' + this.props.id);
                }

            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    render: function () {
        return (
            <p>
                <button onClick={this.handleClick} type="button" className="btn btn-sn btn-success">Hide</button>
            </p>
        );
    }
}),

Comment = React.createClass({
    getInitialState: function () {
        return {liked: true};
    },
    hide_cb: function (job_id) {
        this.setState({liked: !this.state.liked});
    },
    render: function () {
        if (!this.state.liked) {
            return (<p></p>);
        } else {
            var rawMarkup = this.props.children.toString(),
                p = rawMarkup.indexOf('<p>'),
                title = p === -1 ? rawMarkup : rawMarkup.substring(0, p),
                body = p === -1 ? '' : rawMarkup.substring(p);
            return (
                <div className='comment list-group-item'>
                    <span className='label label-info' >
                        <a target="_blank" href={"https://news.ycombinator.com/user?id=" + this.props.author}>{this.props.author}</a>
                    </span>
                    <h4 className="list-group-item-heading" dangerouslySetInnerHTML={{__html: title}}></h4>
                    <div className='list-group-item-text'>
                        <span dangerouslySetInnerHTML={{__html: body}} />
                        <DislikeButton id={this.props.id} url={this.props.url} hide_cb={this.hide_cb}/>
                    </div>
                </div>
            );
        }
    }
}),

CommentList = React.createClass({
    render: function () {
        var url = this.props.url,
            commentNodes = this.props.data.map(function (comment) {
            return (
                <Comment author={comment.by}  key={comment.id} id={comment.id} url={url}>
                    {comment.text}
                </Comment>
            );
        });
        return (
            <div className='commentList list-group'>
                {commentNodes}
            </div>
        );
    }
}),

CommentBox = React.createClass({
    loadCommentsFromServer: function () {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            success: function (data) {
                this.setState({data: data});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    getInitialState: function () {
        return {data: []};
    },
    componentDidMount: function () {
        this.loadCommentsFromServer();
        if (this.props.pollInterval !== undefined) {
            setInterval(this.loadCommentsFromServer, this.props.pollInterval);
        }
    },
    render: function () {
        return (
            <div className='commentBox'>
                <h1>Jobs</h1>
                <CommentList data={this.state.data} url={this.props.url} />
            </div>
        );
    }
});

React.render(
    <CommentBox url='/hnjobs' pollInterval2={2000}/>,
    document.getElementById('content')
);
